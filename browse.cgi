#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI qw/:standard *table *div *td *Tr/;
use CGI::Carp qw(fatalsToBrowser set_message);
use DBI;
use XML::Simple;
use RecipeManager;
use PhraseManager;
use ButtonManager;
$CGI::DISABLE_UPLOADS = 1;

BEGIN {
  sub handle_errors {
    my $message = shift;
    my $quote_prepared = qq#
      <P>An error has occurred:\n</p>
          <P><tt>$message</tt></p>
      <P>The application is unable to continue.\n</p>
      <P>Please contact your administrator for more assistance.\n</p>
      #;
    print($quote_prepared);
  }
set_message(\&handle_errors);
}            

setup_values();
setup_phrases();
setup_buttons();

my $page = new CGI;
my $cgi_name = $page->url();

#-----------------------------------------------------------------

sub print_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$browse_title);

return 1;

}

#-----------------------------------------------------------------

sub perform_search {

my ($sth,$count,$count_select,$data_select,$record_count,@return_array);
my $limit_rows = $_[0];
my $starting_point = $_[1];
local $_;

$count_select = 'select count(*) from recipes';
$data_select = 'select name,id,rating,food_type,'.
               'locked,locked_until,locked_by,locked_session_id '.
               'from recipes order by name';

$sth = $dbh->prepare($count_select);
$sth->execute();

($record_count) = $sth->fetchrow_array();

$sth->finish();
$sth = ();

if($limit_rows)
{
  $data_select .= " limit $starting_point,$number_of_rows_to_display";
}
$sth = $dbh->prepare($data_select);
$sth->execute();

while(my @tmp_array = $sth->fetchrow_array())
{
  push(@return_array,[@tmp_array]);
}

$sth->finish();

return(\@return_array,$record_count);

}

#-----------------------------------------------------------------

sub print_no_records_found {

my $page = $_[0];
local $_;

print $$page->p($$phrases[15]);
print_start_form($page,$cgi_name);
print $$page->p({-align => "center"},add_js_button($page),
                                     main_menu_button($page));
print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub print_buttons {

my $page = $_[0];
local $_;

print $$page->start_div({-class => 'buttons'});

print $$page->p(view_button($page),edit_button($page),delete_button($page),
                add_js_button($page),main_menu_button($page));

print $$page->end_div();

return 1;

}

#-----------------------------------------------------------------

sub get_radio_array {

my ($page,$data) = @_;
my (@id_array,%label_hash,$array,@radio_array,$name);
local $_;

foreach $array (@$data)
{
  $name = $array->[0];
  push(@id_array,$array->[1]);
  $label_hash{$array->[1]} =
    $$page->a({-href =>  "http://$view_cgi?recipe_id=$array->[1]",
               -class => 'plain',
               -title => "View ${name}."},CGI->escapeHTML($name));
}

$$page->autoEscape(0);

@radio_array = $$page->radio_group(-name        => 'recipe_id',
                                   -values      => \@id_array,
                                   -default     => '-',
                                   -labels      => \%label_hash);

$$page->autoEscape(1);


return(\@radio_array);

}



#-----------------------------------------------------------------

sub print_record {

my $page = $_[0];
my $data = $_[1];
my $radio_line = $_[2];
my $class_key = $_[3];
my ($name,$rating,$type);
my $class = 'even-lines';
local $_;

unless($class_key)
{
  $class = 'odd-lines';
}

print $$page->start_Tr({-class => $class});

$name = $data->[0];

print $$page->td($radio_line);

if((defined($data->[2])) && ($data->[2] =~ /\S/o))
{
  $rating = CGI->escapeHTML($data->[2]);
}
else
{
  $rating = '&nbsp;';
}

if(defined($data->[3]) && ($data->[3] =~ /\S/o))
{
  $type = CGI->escapeHTML(get_food_type($data->[3]));
}
else
{
  $type = "&nbsp;";
}
print $$page->td([$rating,$type]);

if(brsrch_determine_record_locked($page,$data->[4],$data->[5],$data->[7]))
{
  my $locked_by_id = $data->[6];
  my $username = reverse_user_id($locked_by_id);
  print $$page->start_td({-align => 'center'});
  print $$page->img({-src => $small_lock_image,
                                 -alt => $$phrases[17]." ".$username,
                                 -title => $$phrases[17]." ".$username
                    }
                   );
  if(this_user_allowed_to_break_lock($page,$locked_by_id))
  {
    print('&nbsp;');
    print($$page->a({-href => "http://$break_lock_cgi?contact_id=$data->[1]",
                     -class => 'plain'},
                     $$page->img({-src          => $small_break_lock_image,
                                  -alt          => $$phrases[18],
                                  -title        => $$phrases[18],
                                  -border       => 0
                                 }
                                )
                   )
         );
  }
  print $$page->end_td();
}
else
{
  print $$page->td('&nbsp;');
}

print $$page->end_Tr();

return 1;

}

#-----------------------------------------------------------------

sub print_page_navigation {

my $page = $_[0];
my $total_records = $_[1];
my ($current_page,$num_pages,$page_count);
local $_;

if(defined($$page->url_param('page')))
{
  $current_page = $$page->url_param('page');
}
else
{
  $current_page = 1;
}

$num_pages = ceil(($total_records / $number_of_rows_to_display));

if($num_pages < 2)
{
  return 2;
}

print $$page->start_div({-class => 'page-navigation'});

if($current_page > 1)
{
  print $$page->a({-class => 'plain',
                   -href => $cgi_name . '?page=' . ($current_page - 1)},
                  "Previous");
}                  

for($page_count = ($current_page - 5);
    (($page_count <= ($current_page + 5)) && ($page_count <= $num_pages));
    $page_count++)
    
{
  if($page_count <= 0)
  {
    $page_count = 1;
  }
  if($page_count == $current_page)
  {
    print($$page->b($current_page));
  }
  else
  {
    print $$page->a({-class => 'plain',
                     -href => $cgi_name . '?page=' . $page_count},
                    " $page_count ");
  }
}  
 
if($current_page == $num_pages)
{
#  print("Last");
}
else
{
  print $$page->a({-class => 'plain',
                   -href => $cgi_name . '?page=' . ($current_page + 1)},
                  "Next");
}

print $$page->end_div();

return 1;

}

#-----------------------------------------------------------------

sub print_recipes {

my $page = $_[0];
my $recipe_select_error_found = $_[1];
my ($data,$class_key,$total_records,$display_all_records,$radio_array,$i,);
local $_;

if((defined($$page->url_param('display_all_records'))) &&
   ($$page->url_param('display_all_records') == 1))
{
     ($data,$total_records) = perform_search(0);
     $display_all_records = 1;
}
else
{
  if(defined($$page->url_param('page')))
  {
    ($data,$total_records) = perform_search(1,
            (($$page->url_param('page') - 1)* $number_of_rows_to_display));
  }
  else
  {
    ($data,$total_records) = perform_search(1,0);
  }
}
if(!defined(@$data))
{
  print_no_records_found($page);
  return 1;
}
else
{
  if($recipe_select_error_found)
  {
    print $$page->p($$page->b({-class => 'brightred'},$$phrases[16]));
  }
  
  print_start_form($page,$cgi_name);

  unless($display_all_records)
  {
    print_page_navigation($page,$total_records);
  }

  print_buttons($page);

  print $$page->start_table({-cellpadding       => 3,
                             -cellspacing       => 3,
                             -border            => 0,
                             -width             => "100%"});

  print $$page->Tr(th(["Name","Rating","Type",
                       "Lock".$$page->br()."Status"]));

  $radio_array = get_radio_array($page,$data);

  $class_key = 1;

  for($i = 0; $i < @$data; $i++)
  {
    $class_key = $class_key ? 0 : 1;
    print_record($page,$data->[$i],$radio_array->[$i],$class_key);
  }

  print $$page->end_table();

  print_buttons($page);
  unless($display_all_records)
  {
    my $capture = print_page_navigation($page,$total_records);
    unless ($capture == 2)
    {
      print $$page->p({-class => "right-align-small"},
                      $$page->a({-class => 'plain',
                                 -href => "$cgi_name?display_all_records=1"},
                                 "Display all $total_records recipes on one page")
                     );
    }
  }
  print $$page->end_form();
}

include_lock_explanation($page);

return 1;

}

#-----------------------------------------------------------------

my $button_value = 0;
my $last_page = $page->referer();

$last_page .= '&select_error=1';

connect_to_db();

if(verify_session_id(\$page))
{
  if(defined($page->param('buttons')))
  {
    $button_value = $page->param('buttons');
  }
  if(defined($page->param('select_error')))
  {
    print_page_header(\$page);
    print_title(\$page);
    print_recipes(\$page,1);
  }
  else
  {
    if(($button_value) && ($button_value eq $$phrases[51]))
    {
      if(defined($page->param('recipe_id')))
      {
        redirect_to_view(\$page,$page->param('recipe_id'));
      }
      else
      {
        print $page->redirect(-uri => $last_page);
      }
    }
    elsif(($button_value) && ($button_value eq $$phrases[53]))
    {
      if(defined($page->param('recipe_id')))
      {
        redirect_to_delete(\$page,$page->param('recipe_id'));
      }
      else
      {
        print $page->redirect(-uri => $last_page);    
      }
    }
    elsif(($button_value) && ($button_value eq $$phrases[52]))
    {
      if(defined($page->param('recipe_id')))
      {
        redirect_to_edit(\$page,$page->param('recipe_id'));
      }
      else
      {
        print $page->redirect(-uri => $last_page);
      }
    }
    else
    {
      print_page_header(\$page);
      print_title(\$page);
      print_recipes(\$page,0);
    }
  }
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
