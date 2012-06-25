#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI qw/:standard *table *Tr *td/;
use CGI::Carp qw(fatalsToBrowser set_message);
use DBI;
use XML::Simple;
use RecipeManager;
use ButtonManager;
use PhraseManager;
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
setup_buttons();
setup_phrases();

my $page = new CGI;
my $cgi_name = $page->url();

#-----------------------------------------------------------------

sub print_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$search_title);

return 1;

}

#-----------------------------------------------------------------

sub get_search_string {

my $page = $_[0];
my ($script_url,$param,@param_array,$search_string);
local $_;

$script_url = $$page->url({-query => 1});
(undef,$param) = split(/$search_results_cgi\?/,$script_url);
@param_array = split(/;/,$param);
foreach $param (@param_array)
{
  if($param =~ /^search_string/o)
  {
    (undef,$search_string) = split(/=/,$param);
    return(\$search_string);
  }
  unless(($param =~ /^search_defined/o) || ($param =~ /^buttons/o) ||
         ($param =~ /^search_string/o) || ($param =~ /^display_all_records/o) ||
         ($param =~ /^page/o) || ($param =~ /^select_error/o))
  {
    $search_string .= $param . "&";
  }
}

transform_search_string(\$search_string);

return(\$search_string);

}
  
#-----------------------------------------------------------------

sub build_search_no_prior {

my $page = $_[0];
my $param_style = $_[1];
my ($field_info,@search_params,$rf_data,$query_string,$function_name,$dump,
    @query_array);
local $_;

@search_params = $$page->${param_style}();

foreach(@search_params)
{
  unless(($_ eq 'search_defined') || ($_ eq 'display_all_records') ||
         ($_ eq 'page') || ($_ eq 'select_error'))
  {
    $field_info = $$form_field_hash{$_};
    if((defined($field_info->{'type'})) &&
       (($field_info->{'type'} eq "function") ||
       ($field_info->{'type'} eq "radio_group")))
    {
      if($field_info->{'type'} eq "radio_group")
      {
        $rf_data = $$page->${param_style}($_);
      }
      else
      {
        $function_name = $field_info->{'results_function'};
        if($function_name)
        {
          $rf_data =
            $form_field_functions{$function_name}->($$page->${param_style}($_));
        }
        else
        {
          $rf_data = $$page->${param_style}($_);
        }
      }
      $query_string .= "AND $_ = ? ";
      push(@query_array,$rf_data);
    }
    else
    {
      $query_string .= "AND $_ LIKE ? ";
      $dump = $$page->${param_style}($_);
      push(@query_array,"%" . $dump . "%");
    }
  }
}
$query_string =~ s/^AND//io;

return(\@query_array,\$query_string);

}


#-----------------------------------------------------------------

sub construct_search_array_hash {

my @params = @_;
my $page = shift(@params);
my $param_style = shift(@params);
my @param_array = ();
my %param_hash = ();
my @working_array = ();
my ($a,$b,$c);
local $_;

foreach(@params)
{
  if($_ eq 'search_string')
  {
    my $string = $$page->${param_style}('search_string');
    reverse_search_string_transform(\$string);
    @working_array = split(/\&/,$string);
    unless(@working_array)
    {
      @working_array = split(/;/,$string);
    }
    foreach $a(@working_array)
    {
      ($b,$c) = split(/=/,$a);
      push(@param_array,$b);
      $param_hash{$b} = $c;
    }
  }
}

return(\@param_array,\%param_hash);

}

#-----------------------------------------------------------------

sub build_search_using_search_string {

my $page = $_[0];
my $param_style = $_[1];
my ($field_info,$search_params,$rf_data,$query_string,$function_name,$dump,
    @query_array,$param_hash);
local $_;

($search_params,$param_hash) =
   construct_search_array_hash($page,$param_style,$$page->${param_style}());

foreach(@$search_params)
{
  unless(($_ eq 'search_defined') || ($_ eq 'page') ||
         ($_ eq 'display_all_records'))
  {
    $field_info = $$form_field_hash{$_};
    if(($field_info->{'type'} eq "function") ||
       ($field_info->{'type'} eq "radio_group"))
    {
      if($field_info->{'type'} eq "radio_group")
      {
        $rf_data = $$param_hash{$_};
      }
      else
      {
        $function_name = $field_info->{'results_function'};
        if($function_name)
        {
          $rf_data =
            $form_field_functions{$function_name}->($$param_hash{$_});
        }
        else
        {
          $rf_data = $$param_hash{$_};
        }
      }
      $query_string .= "AND $_ = ? ";
      push(@query_array,$rf_data);
    }
    else
    {
      $query_string .= "AND $_ LIKE ? ";
      $dump = $$param_hash{$_};
      push(@query_array,"%" . $dump . "%");
    }
  }
}
$query_string =~ s/^AND//io;

return(\@query_array,\$query_string);

}

#-----------------------------------------------------------------

sub conduct_search {

my $page = $_[0];
my $limit_rows = $_[1];
my $starting_point = $_[2];
my ($sth,$query_array,$param_style,$sql,$query_string,$matching_records,
    @tmp_array,@return_array);
local $_;

if(defined($$page->url_param('search_defined')))
{
  $param_style = "url_param";
}
else
{
  $param_style = "param";
}

if(defined($$page->${param_style}('search_string')))
{
  ($query_array,$query_string) =
        build_search_using_search_string($page,$param_style);
}
else
{
  ($query_array,$query_string) = build_search_no_prior($page,$param_style);
}

$sql = "select count(*) from recipes where $$query_string";
$sth = $dbh->prepare($sql);
$sth->execute(@$query_array);


($matching_records) = $sth->fetchrow_array();

$sth->finish();
$sql = "select name,id,rating,food_type,locked,locked_by,locked_until," .
       "locked_session_id from recipes " .
       "where $$query_string order by name";
if($limit_rows)
{
  $sql .= " limit $starting_point,$number_of_rows_to_display";
}
$sth = $dbh->prepare($sql);
$sth->execute(@$query_array);

while(my @tmp_array = $sth->fetchrow_array())
{
  push(@return_array,[@tmp_array]);
}

$sth->finish();

return(\@return_array,$matching_records);

}

#-----------------------------------------------------------------

sub print_buttons {

my $page = $_[0];
local $_;

print($$page->p(view_button($page),
                edit_button($page),
                delete_button($page),
                add_js_button($page),
                new_search_button($page),
                main_menu_button($page)
               )
      );

return 1;

}

#-----------------------------------------------------------------

sub print_no_records_found {

my $page = $_[0];
local $_;

print $$page->p({-align => "center"}, $$phrases[37]);

print $$page->p({-align => "center"},new_search_button($page),
                                     main_menu_button($page));

return 1;

}

#-----------------------------------------------------------------

sub get_radio_array {

my ($page,$search_string,$data) = @_;
my (@id_array,%label_hash,$array,@radio_array,$name);
local $_;

foreach $array (@$data)
{
  $name = $array->[0];
  push(@id_array,$array->[1]);
  $label_hash{$array->[1]} =
    $$page->a({-href =>  "http://$view_cgi?recipe_id=$array->[1]&search_defined=1&search_string=$$search_string",
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

sub include_hidden_fields {

my $page = $_[0];
my $search_string = $_[1];
local $_;

print $$page->hidden(-name => "search_defined",
                       -default => 1);
print $$page->hidden(-name => "search_string",
                       -default => $$search_string);

return 1;

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

if(brsrch_determine_record_locked($page,$data->[4],$data->[6],$data->[7]))
{
  my $locked_by_id = $data->[5];
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
    print($$page->a({-href => "http://$break_lock_cgi?recipe_id=$data->[1]",
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
my $search_string = $_[2];
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
                   -href => $cgi_name . '?search_defined=1&search_string='.$$search_string.'&page=' . ($current_page - 1)},
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
                     -href => $cgi_name . '?search_defined=1&search_string='.$$search_string.'&page=' . $page_count},
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
                   -href => $cgi_name . '?search_defined=1&search_string='.$$search_string.'&page=' . ($current_page + 1)},
                  "Next");
}

print $$page->end_div();

return 1;

}

#-----------------------------------------------------------------

sub print_recipes {

my $page = $_[0];
my $recipe_select_error_found = $_[1];
my $search_string = get_search_string($page);
my ($data,$class_key,$total_records,$display_all_records,$radio_array,$i,);
local $_;

if((defined($$page->url_param('display_all_records'))) &&
   ($$page->url_param('display_all_records') == 1))
{
     ($data,$total_records) = conduct_search($page,0);
     $display_all_records = 1;
}
else
{
  if(defined($$page->url_param('page')))
  {
    ($data,$total_records) = conduct_search($page,1,
            (($$page->url_param('page') - 1)* $number_of_rows_to_display));
  }
  else
  {
    ($data,$total_records) = conduct_search($page,1,0);
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
    print_page_navigation($page,$total_records,$search_string);
  }

  print_buttons($page);

  print $$page->start_table({-cellpadding       => 3,
                             -cellspacing       => 3,
                             -border            => 0,
                             -width             => "100%"});

  print $$page->Tr(th(["Name","Rating","Type",
                       "Lock".$$page->br()."Status"]));

  $radio_array = get_radio_array($page,$search_string,$data);

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
    my $capture = print_page_navigation($page,$total_records,$search_string);
    unless ($capture == 2)
    {
      print $$page->p({-class => "right-align-small"},
                      $$page->a({-class => 'plain',
                                 -href => "$cgi_name?display_all_records=1&search_defined=1&search_string=$$search_string"},
                                 "Display all $total_records matching recipes on one page")
                     );
    }
  }
  include_hidden_fields($page,$search_string);
  print $$page->end_form();
}

include_lock_explanation($page);

return 1;

}

#-----------------------------------------------------------------

my $button_value = 0;
my $search_defined = 0;
my $last_page = $page->referer();

$last_page .= '&select_error=1';

connect_to_db();

if(verify_session_id(\$page))
{
  if((defined($page->url_param('search_defined'))) ||
     ($page->param('search_defined')))
  {
    $search_defined = 1;
  }
  if($search_defined)
  {
    if(defined($page->param('select_error')))
    {
      print_page_header(\$page);
      print_title(\$page);
      print_recipes(\$page,1);
    }
    else
    {
      if(defined($page->param('buttons')))
      {
        $button_value = $page->param('buttons');
      }
      if(($button_value) && ($button_value eq $$phrases[51]))
      {
        if(defined($page->param('recipe_id')))
        {
          redirect_to_view(\$page,$page->param('recipe_id'),$page->param('search_string'));
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
          redirect_to_delete(\$page,$page->param('recipe_id'),$page->param('search_string'));
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
          redirect_to_edit(\$page,$page->param('recipe_id'),$page->param('search_string'));
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
    redirect_to_search(\$page);
  }
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
