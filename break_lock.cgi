#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI;
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

sub print_page_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$break_lock_title);

return 1;

}

#-----------------------------------------------------------------

sub print_break_lock_advisory_page {

my $page = $_[0];
local $_;

print $$page->p([$$phrases[38],$$phrases[39]]);

print($$page->ul($$page->li([$$phrases[40],$$phrases[41],$$phrases[42],
                             $$phrases[43]])
                )
     );

print $$page->p({-class => 'action-confirm'},$$phrases[44]);

print $$page->p([$$phrases[45],$$phrases[46]]);

print_start_form($page,$cgi_name);

print $$page->p($$page->submit(-name    => 'buttons',
                               -value   => $$phrases[47]),
                back_js_button($page),
                main_menu_button($page));

if(defined($$page->url_param('search_defined')))
{
  include_back_to_search($page);
}

include_hidden_fields($page);

print $$page->end_form();                

return 1;

}
 
#-----------------------------------------------------------------

sub include_hidden_fields {

my $page = $_[0];
local $_;

if((defined($$page->url_param('search_defined'))) &&
   ($$page->url_param('search_defined') == 1))
{
  print $$page->hidden(-name => 'search_defined',
                       -default => 1);
  print $$page->hidden(-name => 'search_string',
                       -default => $$page->url_param('search_string'));
}

if(defined($$page->url_param('display_all_rows')))
{
  print $$page->hidden(-name    => 'display_all_rows',
                       -default => 1);
}
elsif(defined($$page->url_param('page')))
{
  print $$page->hidden(-name    => 'page',
                       -default => $$page->url_param('page'));
}

print $$page->hidden(-name => 'recipe_id',
                     -default => $$page->url_param('recipe_id'));

return 1;

}

#-----------------------------------------------------------------

sub print_lock_released {

my $page = $_[0];
local $_;

print $$page->p([$$phrases[48],$$phrases[49]]);

print_start_form($page,$cgi_name);

print $$page->p(edit_js_button($page),delete_js_button($page),view_button($page),
                main_menu_button($page));
                
if(defined($$page->param('search_defined')))
{
  include_back_to_search($page);
}

include_hidden_fields($page);

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub print_problem_releasing_lock {

my $page = $_[0];
local $_;

print $$page->p([$$phrases[50],main_menu_button($page)]);

return 1;

}

#-----------------------------------------------------------------

my $button_value = '';

connect_to_db();

if(verify_session_id(\$page))
{
  if(defined($page->param('buttons')))
  {
    $button_value = $page->param('buttons');
  }

  if(($button_value) && ($button_value eq $$phrases[47]))
  {
  
    if(defined($page->param('recipe_id')))
    {
      if(release_lock($page->param('recipe_id')))
      {
        print_page_header(\$page,0,1,$page->param('recipe_id'));
        print_page_title(\$page);
        print_lock_released(\$page);
      }
      else
      {
        print_page_header(\$page);
        print_page_title(\$page);
        print_problem_releasing_lock(\$page);
      }
    }
    else
    {
      print_problem_releasing_lock(\$page);
    }
    print $page->end_html();
  }
  elsif(($button_value) && ($button_value eq $$phrases[51]))
  {
    redirect_to_view(\$page);
  }
  elsif(($button_value) && ($button_value eq $$phrases[52]))
  {
    redirect_to_edit(\$page);
  }
  elsif(($button_value) && ($button_value eq $$phrases[53]))
  {
    redirect_to_delete(\$page);
  }
  else
  {
    print_page_header(\$page);
    print_page_title(\$page);
    print_break_lock_advisory_page(\$page);
    print $page->end_html();
  }
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();