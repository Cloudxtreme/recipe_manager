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

sub print_buttons {

my $page = $_[0];
local $_;

print $$page->p(search_button($page),reset_button($page),
                main_menu_button($page));

return 1;

}

#-----------------------------------------------------------------

sub print_search_form {

my $page = $_[0];
my $no_search_found_error = $_[1];
my ($old_recipe_title,$quote_prepared,$field_form,$field_info,
    $field_name,$field_type,$label);
local $_;

print_page_header($page);
print_title($page);
                        
if($no_search_found_error)
{
  print $$page->p($$page->b({-class => 'brightred'},$$phrases[95]));
}
        

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
  print $$page->start_Tr();
  print $$page->td({-class => 'recipe-add-label'},
                   $field_info->{'label'});
  print $$page->start_td({-class => 'recipe-add-field'});

  if($field_type eq "textfield")
  {
    print $$page->textfield(-name 	=> $field_name,
                            -size 	=> $field_info->{'size'},
                            -maxlength	=> $field_info->{'maxlength'}
                           );
  }
  elsif($field_type eq "textarea")
  {
    print $$page->textarea(-name	=> $field_name,
    			   -rows	=> $field_info->{'rows'},
    			   -columns	=> $field_info->{'columns'}
    			  );
  }
  elsif($field_type eq "radio_group")
  {
    my $radio_values = get_radio_values($field_info,1);
    print $$page->radio_group(-name		=> $field_name,
    		              -linebreak	=> $field_info->{'linebreak'},
    		              -values		=> $$radio_values[0],
    		              -labels		=> $$radio_values[1],
    		              -default		=> 0
    		             );
  }
  elsif($field_type eq "function")
  {
    my $function_name = $field_info->{'add_function'};
    
    $form_field_functions{$function_name}->($page,$field_info,$field_name);
  }
  print $$page->end_td();
  print $$page->end_Tr();
}

print $$page->end_table();

print_buttons($page);

print $$page->end_form();
print $$page->end_html();

return 1;

}

#-----------------------------------------------------------------

sub compile_search_directives {

my $page = $_[0];
my ($field,$url_string,$field_info);
local $_;

$url_string = "search_defined=1";

foreach $field (@$form_field_order)
{
  $field_info = $$form_field_hash{$field};
  if((defined($$page->param($field))) && ($$page->param($field) =~ /\S/o))
  {
    if(defined($field_info->{'field_ignore'}))
    {
      if($$page->param($field) ne $field_info->{'field_ignore'})
      {
        $url_string .= "&" . $field . "=" . remove_trailing_whitespace($$page->param($field));
      }
      else
      {
        next;
      }
    }
    else
    {
      $url_string .= "&" . $field . "=" . remove_trailing_whitespace($$page->param($field));
    }
  }
}

return(\$url_string);

}

#-----------------------------------------------------------------

my $start_search = 0;

connect_to_db();

if(verify_session_id(\$page))
{
  if(defined($page->param("buttons")) && ($page->param('buttons') eq $$phrases[36]))
  {
      $start_search = 1;
  }  
  if($start_search)
  {
    my $search_string = compile_search_directives(\$page);
    if ($$search_string eq "search_defined=1")
    {
      print_search_form(\$page,1);
    }
    else
    {
      redirect_to_results(\$page,$search_string);
    }
  }
  else
  {
    print_search_form(\$page,0);
  }
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
