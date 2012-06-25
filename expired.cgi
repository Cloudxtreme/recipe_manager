#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser set_message);
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

#-----------------------------------------------------------------

sub print_expired_page {

my $page = $_[0];
local $_;

print $$page->h1({-align => "center"},$login_title);

print $$page->p({-class => "login-error"},[$$phrases[5],$$phrases[6]]);
print_start_form($page,"http://$auth_cgi");

print $$page->p({-align => "center"},$$phrases[2],
                $$page->textfield(-name => "username",
                                 -maxlength => 32,
                                 -size => 32,
                                 -override => 1,
                                 -default => "")
               );
print $$page->p({-align => "center"},$$phrases[3],
                $$page->password_field(-name => "password",
                                 -maxlength => 32,
                                 -size => 32,
                                 -override => 1,
                                 -default => "")
               );
print $$page->hidden(-name => "hippo", -default => "1");
print $$page->p({-align => "center"},login_button($page),reset_button($page));
print $$page->end_form();
                

}

#-----------------------------------------------------------------

my $page = new CGI;

print_page_header(\$page,1);
print_expired_page(\$page);
print $page->end_html();
