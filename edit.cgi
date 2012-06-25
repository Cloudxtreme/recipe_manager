#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI qw/:standard *table *Tr *td/;
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

print $$page->h2({-class => 'title'},$edit_title);

return 1;

}

#-----------------------------------------------------------------

sub print_buttons {

my $page = $_[0];
local $_;

print $$page->p(save_button($page),cancel_button($page),reset_button($page));

return 1;

}


#-----------------------------------------------------------------

sub print_edit_form {

my $page = $_[0];
my $recipe_id = $_[1];
my ($sth,$results,$field_form,$field_info,$field_name,$field_default,
    $field_type,$sql,$label,$name);
local $_;

print_start_form($page,$cgi_name);

print_buttons($page);

print $$page->start_table({-cellpadding       => 3,
                           -border            => 0,
                           -width             => "100%",
                           -cellspacing       => 3});
$sql = "select * from recipes where id = ?";
$sth= $dbh->prepare($sql);

$sth->execute($recipe_id);

$results = $sth->fetchrow_hashref();

foreach $field_form (@$form_field_order)
{
  $field_info = $$form_field_hash{$field_form};
  $field_name = $field_form;
  $field_type = $field_info->{'type'};
  print $$page->start_Tr();
  print $$page->td({-class => 'recipe-add-label'},
                   $field_info->{'label'});
  print $$page->start_td({-class => 'recipe-add-field'});

  if($field_type eq "textfield")
  {
    if(defined($results->{$field_name}))
    {
      $field_default = $results->{$field_name};
    }
    else
    {
      $field_default = "";
    }
    print $$page->textfield(-name 	=> $field_name,
                            -size 	=> $field_info->{'size'},
                            -maxlength	=> $field_info->{'maxlength'},
                            -default	=> $field_default
                           );
    if($field_name eq 'name')
    {
      $name = $field_default;
    }
 
  }
  elsif($field_type eq "textarea")
  {
    if(defined($results->{$field_name}))
    {
      $field_default = $results->{$field_name};
    }
    else
    {
      $field_default = "";
    }
    print $$page->textarea(-name	=> $field_name,
    			   -rows	=> $field_info->{'rows'},
    			   -columns	=> $field_info->{'columns'},
    			   -default	=> $field_default
    			  );
  }
  elsif($field_type eq "radio_group")
  {
    my $radio_values = get_radio_values($field_info);
    if(defined($results->{$field_name}))
    {
      $field_default = $results->{$field_name};
    }
    else
    {
      $field_default = $field_info->{'default'};
    }
    print $$page->radio_group(-name		=> $field_name,
    		              -linebreak	=> $field_info->{'linebreak'},
    		              -default		=> $field_default,
    		              -values		=> $$radio_values[0],
    		              -labels		=> $$radio_values[1]
    		             );
  }
  elsif($field_type eq "function")
  {
    my $function_name = $field_info->{'edit_function'};
    
    $form_field_functions{$function_name}->($page,$field_info,$field_name,$results->{$field_name});
  }
  print $$page->end_td();
  print $$page->end_Tr();
}

print $$page->end_table();

include_hidden_fields($page,$recipe_id,$name);

print_buttons($page);

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub include_hidden_fields {

my $page = $_[0];
local $_;

print $$page->hidden(-name      => 'recipe_verify',
                     -default   => 1);

print $$page->hidden(-name      => "recipe_id",
                     -default   => $_[1]);

print $$page->hidden(-name      => "recipe_name",
                     -default   => $_[2]);

if(defined($$page->url_param('search_defined')))
{
   print $$page->hidden(-name    => 'search_defined',
                        -default => 1);
   print $$page->hidden(-name    => 'search_string',
                        -default => $$page->url_param('search_string'));
}



return 1;

}

#-----------------------------------------------------------------

sub print_edit_cancelled {

my $page = $_[0];
my $unquoted_recipe_name = $$page->param('recipe_name');
my $recipe_name;
local $_;

$recipe_name = CGI->escapeHTML($unquoted_recipe_name);

print $$page->p($$phrases[20],
                $$page->b({-class => 'royalblue'},$recipe_name),
                $$phrases[21]);


print_start_form($page,$cgi_name);

print $$page->p(main_menu_button($page));

if(defined($$page->param('search_defined')))
{
  include_back_to_search($page);
}

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub show_edit_completed {

my $page = $_[0];
my $recipe_name = $$page->param('name');
my $quote_prepared;
local $_;

$recipe_name = CGI->escapeHTML($recipe_name);


print $$page->p($$page->b({-class => 'royalblue'},$recipe_name),
                $$phrases[22]);

print_start_form($page,$cgi_name);

print $$page->p(main_menu_button($page));


if(defined($$page->param('search_defined')))
{
  include_back_to_search($page);
}

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub edit_recipe {

my $page = $_[0];
my $recipe_id = $_[1];
my ($ok,$quote_prepared,$sth,$field,@value_array,$field_string);
local $_;

$field_string = "";

foreach $field (@$form_field_order)
{
  $field_string .= "$field = ?,";
  push(@value_array,$$page->param($field));
}

$field_string =~ s/,$//o;

$sth = $dbh->prepare("update recipes set $field_string where id = $recipe_id");

$ok = $sth->execute(@value_array);

unless($ok)
{
  die("There was an error updating a recipe in the db:  $!\n");
}     

return 1;

}

#-----------------------------------------------------------------

sub verify_edit_for_errors {

my $page = $_[0];
my $error_found = 0;
my @errors_found;
local $_;

unless((defined($$page->param('name'))) && ($$page->param('name') =~ /\w{2,}/io))
{
  $error_found = 1;
  push(@errors_found,$$phrases[10]);
}
unless((defined($$page->param('ingredients'))) && 
       ($$page->param('ingredients') =~ /\w.\w./o))
{
  $error_found = 1;
  push(@errors_found,$$phrases[11]);
}

unless((defined($$page->param('directions'))) &&
       ($$page->param('directions') =~ /\w.\w./o))
{
  $error_found = 1;
  push(@errors_found,$$phrases[12]);
}

return([$error_found,\@errors_found]);

}

#-----------------------------------------------------------------

sub print_fix_errors {

my $page = $_[0];
my $recipe_id = $_[1];
my $error_array = $_[2];
my @local_error_array;
local $_;

print $$page->p({-class => "verify-errors"},$$phrases[13]);
print $$page->ul($$page->li({-type      => 'disc',
                             -class     => 'verify-errors'},$error_array));
print $$page->p({-class => "verify-errors"},$$phrases[14]);
print_edit_form($page,$recipe_id);

return 1;

}


#-----------------------------------------------------------------

my $recipe_id = 0;
my $edit_shown = 0;
my $edit_verify = ();
my $commit_edit = 0;

connect_to_db();

if(verify_session_id(\$page))
{
  if(defined($page->url_param('recipe_id')))
  {
    $recipe_id = $page->url_param('recipe_id');
  }
  elsif(defined($page->param('recipe_id')))
  {
    $recipe_id = $page->param('recipe_id');
  }
  if(($recipe_id) && (redirect_if_locked(\$page,$recipe_id)))
  {
    goto CGI_END;
  }
  establish_lock(\$page,$recipe_id);
  if(defined($page->param('recipe_verify')))
  {
    $edit_shown = $page->param('recipe_verify');
  }
  if(defined($page->param("buttons")))
  {
    if($page->param('buttons') eq "Save")
    {
      $commit_edit = 1;
    }
    elsif($page->param('buttons') eq "Cancel")
    {
      $commit_edit = 2;
    }
  }  
  if(($recipe_id) && ($edit_shown) && ($commit_edit == 1))
  {
    $edit_verify = verify_edit_for_errors(\$page);
  }
  if(($recipe_id) && ($commit_edit == 1) && ($edit_shown) && (!($$edit_verify[0])))
  {
    edit_recipe(\$page,$recipe_id);
    release_lock($recipe_id);
    print_page_header(\$page);
    print_title(\$page);
    show_edit_completed(\$page);
    print $page->end_html();
  }
  elsif(($recipe_id) && ($commit_edit == 1) && ($edit_shown) && ($$edit_verify[0]))
  {
    print_page_header(\$page);
    print_title(\$page);
    print_fix_errors(\$page,$recipe_id,$$edit_verify[1]);
    print $page->end_html();
  }
  elsif(($recipe_id) && ($commit_edit == 2) && ($edit_shown))
  {
    release_lock($recipe_id);
    print_page_header(\$page);
    print_title(\$page);
    print_edit_cancelled(\$page);
    print $page->end_html();
  }
  elsif($recipe_id)
  {
    print_page_header(\$page);
    print_title(\$page);
    print_edit_form(\$page,$recipe_id);
    print $page->end_html();
  }
  else
  {
    no_parameter_found(\$page);
  }
}
else
{
  print_session_expired_page(\$page);
}

CGI_END:  disconnect_from_db();
