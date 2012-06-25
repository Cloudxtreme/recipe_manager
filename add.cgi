#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI qw/:standard *table/;
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
setup_buttons();
setup_phrases();

my $page = new CGI;
my $cgi_name = $page->url();

#-----------------------------------------------------------------

sub print_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$add_title);

return 1;

}

#-----------------------------------------------------------------

sub print_buttons {

my $page = $_[0];
local $_;

print $$page->p(add_button($page),reset_button($page),main_menu_button($page));

return 1;

}

#-----------------------------------------------------------------

sub print_insertion_form {

my $page = $_[0];
my ($quote_prepared,$field_form,$field_info,$field_name,$field_type,
    $field_default,$label);
local $_;

print_start_form($page,$cgi_name);

print_buttons($page);

print $$page->start_table({-cellpadding		=> 3,
			   -cellspacing		=> 3,
			   -border		=> 0,
			   -width		=> "100%"
			 });

foreach $field_form (@$form_field_order)
{
  $field_info = $$form_field_hash{$field_form};
  $field_name = $field_form;
  $field_type = $field_info->{'type'};
  $label = CGI->escapeHTML($field_info->{'label'});
  print("<tr>\n<td class=\"recipe-add-label\">\n$label\n</td>");
  print("<td class=\"recipe-add-field\">\n");
  if($field_type eq "textfield")
  {
    if(defined($field_info->{'default'}))
    {
      $field_default = $field_info->{'default'};
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
  }
  elsif($field_type eq "textarea")
  {
    if(defined($field_info->{'default'}))
    {
      $field_default = $field_info->{'default'};
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
    print $$page->radio_group(-name		=> $field_name,
    		              -linebreak	=> $field_info->{'linebreak'},
    		              -default		=> $field_info->{'default'},
    		              -values		=> $$radio_values[0],
    		              -labels		=> $$radio_values[1]
    		             );
  }
  elsif($field_type eq "function")
  {
    my $function_name = $field_info->{'add_function'};
    $form_field_functions{$function_name}->($page,$field_info,$field_name);
  }
  print("</td>\n");
}

print $$page->end_table();

print $$page->hidden(-name	=> "recipe_verify",
                     -default	=> "1");

print_buttons($page);

print $$page->end_form();               

return 1;

}

#-----------------------------------------------------------------

sub insert_recipe_into_db {

my $page = $_[0];
my ($ok,$quote_prepared,$sth,$field,$value_placeholders,@value_array,
    $field_string,$working_value);
local $_;

$value_placeholders = $field_string = "";

foreach $field (@$form_field_order)
{
  $field_string .= $field.",";
  push(@value_array,$$page->param($field));
  $value_placeholders .= "?,";
}

$field_string =~ s/,$//o;
$value_placeholders =~ s/,$//o;

$sth = $dbh->prepare("insert recipes ($field_string) values ($value_placeholders)");

$ok = $sth->execute(@value_array);

unless($ok)
{
  die("There was an error inserting the recipe into the db:  $!\n");
}     

return 1;

}

#-----------------------------------------------------------------

sub print_successful_insertion {

my $page = $_[0];
my $name = $$page->param('name');
local $_;

print_start_form($page,$cgi_name);

$name = CGI->escapeHTML($name);

print $$page->p($$phrases[7]);
print $$page->p($$page->b({-class => 'royalblue'},$name));
print $$page->p($$phrases[8],$$phrases[59]);
print $$page->p(add_button($page),main_menu_button($page));
print $$page->end_form();

return 1;

}

#----------------------------------------------------------------------------

sub verify_add_information {

my $page = $_[0];
my (@array_to_return,$verified_ok,@error_array,$name,$ingredients,$directions);
local $_;

if(defined($$page->param('name')))
{
  $name = $$page->param('name');
  unless($name =~ /\w.\w./o)
  {
    push(@error_array,$$phrases[9]);
  }
}
else
{
  push(@error_array,$$phrases[10]);
}

if(defined($$page->param('ingredients')))
{
  $ingredients = $$page->param('ingredients');
  unless($ingredients =~ /\w.\w./o)
  {
    push(@error_array,$$phrases[11]);
  }
}
else
{
  push(@error_array,$$phrases[11]);
}

if(defined($$page->param('directions')))
{
  $directions = $$page->param('directions');
  unless($directions =~ /\w.\w./o)
  {
    push(@error_array,$$phrases[12]);
  }
}
else
{
  push(@error_array,$$phrases[12]);
}

if(@error_array)
{
  push(@array_to_return,0);
  push(@array_to_return,\@error_array);
}
else
{
  push(@array_to_return,1);
}

return(\@array_to_return);

}  

#----------------------------------------------------------------------------

sub print_fix_errors {

my $page = $_[0];
my $error_array = $_[1];
my @local_error_array;
local $_;

print $$page->p({-class => "verify-errors"},$$phrases[13]);
print $$page->ul($$page->li({-type 	=> 'disc',
                             -class	=> 'verify-errors'},$error_array));
print $$page->p({-class => "verify-errors"},$$phrases[14]);
print_insertion_form($page);

return 1;

}                

#----------------------------------------------------------------------------

my $button_value = 0;

connect_to_db();

if(verify_session_id(\$page))
{
  print_page_header(\$page);
  if(defined($page->param('buttons')))
  {
    $button_value = $page->param('buttons');
  }
  print_title(\$page);
  if(($button_value) && ($button_value eq "Add"))
  {
    my $recipe_verify = 0;
    if(defined($page->param('recipe_verify')))
    {
      $recipe_verify = $page->param('recipe_verify');
    }
    if($recipe_verify)
    {
      my $verify_information = verify_add_information(\$page);
      if($$verify_information[0])
      {
        if(insert_recipe_into_db(\$page))
        {
          print_successful_insertion(\$page);
        }
      }
      else
      {
        print_fix_errors(\$page,$$verify_information[1]);
      }
    }
    else
    {
      print_insertion_form(\$page);
    }
  }
  else
  {
    print_insertion_form(\$page);
  }
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
