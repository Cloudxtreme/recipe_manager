#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI v3.00;
use CGI::Carp qw(fatalsToBrowser set_message);
use CGI::Cookie;
use DBI;
use XML::Simple;
use Digest::MD5;
use RecipeManager;
use PhraseManager;
use ButtonManager;
srand;
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

sub purge_old_sessions {

my $old_session_value = time() - $session_timeout;
my($sth,$db_row,$ok,$sql,$sth2,$session_id);
local $_;

$sql = "select * from recipe_sessions";
$sth = $dbh->prepare($sql);
$sth->execute();

$sql = "delete from recipe_sessions where session_id = ?";
$sth2 = $dbh->prepare($sql);

while($db_row = $sth->fetchrow_hashref())
{
  if($old_session_value >= $db_row->{"session_time"})
  {
    $session_id = $db_row->{'session_id'};
    $ok = $sth2->execute($session_id);
    unless($ok == 1)
    {
      die("Session $db_row->{'session_id'} to be deleted by purge_old_sessions not found in db.\n");
    }
  }
}

$sth->finish();

return 1;

}

#-----------------------------------------------------------------

sub create_hash {

my $given_password = $_[0];
my $md5_obj = Digest::MD5->new;
my $given_password_hash = 0;
local $_;

if(defined($given_password))
{
  chomp($given_password); # Just to be safe
  $md5_obj->add($given_password);
  $given_password_hash = $md5_obj->hexdigest();
}

return($given_password_hash);

}

#-----------------------------------------------------------------

sub get_db_hash {

my $username = $_[0];
my ($sth,$results,$sql_statement);
local $_;

if(defined($username))
{
  $sql_statement = "select password from recipe_users where username = ?";
  $sth = $dbh->prepare($sql_statement);
  $sth->execute($username);
  $results = $sth->fetchrow_hashref();

  if($results->{"password"})
  {
    $sth->finish();
    return($results->{"password"});
  }
  else
  {
    $sth->finish();
    return(110);
  }
}
else
{
  return(109);
}

}

#-----------------------------------------------------------------

sub generate_session_id {

my $input = time() + rand(10000) + 14.2;
my $md5_obj = Digest::MD5->new;
my $session_id;
local $_;


$md5_obj->add($input);
$session_id = $md5_obj->hexdigest();
return($session_id);

}

#-----------------------------------------------------------------

sub store_session_information {

my $username = $_[0];
my $session_id = $_[1];
my ($ok,$sth,$user_id,$results,$sql_statement);
my $unix_time = time();
local $_;

$sql_statement = "select id from recipe_users where username = ?";
$sth = $dbh->prepare($sql_statement);
$sth->execute($username);
$results = $sth->fetchrow_hashref();

if($results->{"id"})
{
  $sth->finish();
  $user_id = $results->{"id"};
}
else
{
  $sth->finish();
  die("No id found for $username in store_session_information.\n");
}

$sth->finish();                     
$sql_statement = "insert recipe_sessions (session_id,user_id,session_time)"
                 . " values (?,?,?)";
$sth = $dbh->prepare($sql_statement);
$ok = $sth->execute($session_id,$user_id,$unix_time);
if(!$ok)
{
  die("Insert statement in store_session_information did not affect any rows.\n");
}
else
{
  return($user_id);
}                

}

#-----------------------------------------------------------------

sub print_login_page {

my $page = $_[0];
my $login_failed_flag = $_[1];
local $_;

print $$page->h1({-align => "center"},$login_title);

if($login_failed_flag)
{
  print $$page->p({-class => "login-error"},$$phrases[0]);
  print $$page->p({-class => "login-error"},$$phrases[1]);
}

print_start_form($page,$cgi_name);
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

sub login_not_successful {

my $page = $_[0];

print_page_header($page,1);
print_login_page($page,1);
print $$page->end_html();

}

#-----------------------------------------------------------------

my ($username, $stored_password_hash,$given_password_hash);

if((defined($page->param("hippo"))) && ($page->param("hippo") eq "1"))
{
  if((defined($page->param("username"))) && (defined($page->param("password"))))
  {
    connect_to_db();
  
    $username = $page->param("username");
    $stored_password_hash = get_db_hash($username);
    $given_password_hash = create_hash($page->param("password"));

    if($given_password_hash eq $stored_password_hash)
    {
      my $session_id = generate_session_id();
      purge_old_sessions();
      my $user_id = store_session_information($username,$session_id);
      my $cookie_one = new CGI::Cookie(-name => $session_cookie,
                                       -value => $session_id);
      my $cookie_two = new CGI::Cookie(-name => $id_cookie,
                                       -value => $user_id);                                 
      print("Set-Cookie: ".$cookie_one->as_string()."\n");
      print("Set-Cookie: ".$cookie_two->as_string()."\n");
      print $page->redirect("http://$menu_cgi");
    }
    else
    {
      login_not_successful(\$page);
    }
    disconnect_from_db();
  }
  else
  {
    login_not_successful(\$page);
  }
}
else
{
  print_page_header(\$page,1);
  print_login_page(\$page,0);
  print $page->end_html();
}
