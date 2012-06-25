#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI::Carp qw(fatalsToBrowser set_message);
use CGI;
use DBI;
use XML::Simple;
use RecipeManager;
use ButtonManager;
use PhraseManager;

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

$CGI::DISABLE_UPLOADS = 1;

setup_values();
setup_buttons();
setup_phrases();

my $page = new CGI;
my $cgi_name = $page->url();

#-----------------------------------------------------------------

sub remove_session_from_db {

my $session_id = $_[0];
my $user_id = $_[1];
my ($ok,$sql,$sth,$username);
local $_;

$sql = "delete from recipe_sessions where session_id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($session_id);

if(!$ok)
{
  warn("Could not delete $session_id from sessions table:  $!\n");
}

$sql = "select username from recipe_users where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($user_id);

$username = $sth->fetchrow_array();

$sth->finish();

unless(defined($username))
{
  $username = '';
}

return $username;

}

#-----------------------------------------------------------------

sub print_logged_out_page {

my $page = $_[0];
my $username = $_[1];
local $_;

print_page_header($page,1);

print $$page->h1({-align => "center"},$login_title);
print $$page->p({-class => "logout"},$$phrases[4]);
print_start_form($page,"http://$auth_cgi");
print $$page->p({-align =>"center"},$$phrases[2],
                $$page->textfield(-name => "username",
                                 -default => "$username",
                                 -size => 32,
                                 -maxlength => 32));
print $$page->p({-align => "center"},$$phrases[3],
                $$page->password_field(-name => "password",
                                       -default => "",
                                       -override => 1,
                                       -size => 32,
                                       -maxlength => 32));
print $$page->hidden(-name => "hippo",-default => "1");                                       
print $$page->p({-align => "center"},submit_button($page),reset_button($page));
return 1;

}

#-----------------------------------------------------------------

connect_to_db();

my $username = remove_session_from_db($page->cookie($session_cookie),
                                      $page->cookie($id_cookie));
print_logged_out_page(\$page,$username);

disconnect_from_db();
