#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser set_message);
use DBI;
use XML::Simple;
use Digest::MD5;
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

print $$page->h2({-class => 'title'},$password_title);

return 1;

}

#-----------------------------------------------------------------

sub print_change_form {

my $page = $_[0];
my $password_errors = $_[1];
my $user_id = $$page->cookie($id_cookie);
my ($sth,$username,$name,$results,$sql_prepared);
local $_;

if($password_errors)
{
  foreach(@$password_errors)
{
  if($_ == 1)
  {
    print $$page->p({-class => "password-match-error"},$$phrases[73]);
  }
  elsif($_ == 2)
  {
    print $$page->p({-class => "password-match-error"},"$$phrases[74] $min_password_length $$phrases[75]");
  }
  elsif($_ == 3)
  {
    print $$page->p({-class => "password-match-error"},$$phrases[76]);
  }
}

}

$sql_prepared = "select * from recipe_users where id = ?";
$sth = $dbh->prepare($sql_prepared);
$sth->execute($user_id);

$results = $sth->fetchrow_hashref();

if(defined($results))
{
  $username = $results->{'username'};
  $name = $results->{'name'};
  $sth->finish();
}
else
{
  die("Could not get basic information on user_id $user_id from db:  $!\n");
}

print $$page->p($$phrases[77]);
print_start_form($page,$cgi_name);
print $$page->p("$$phrases[78] $name ($username):&nbsp; \n",
                $$page->password_field(-name           => "first_new_password",
                                       -size           => 32,
                                       -default        => "",
                                       -override       => 1,
                                       -maxlength      => 32));
print $$page->p("$$phrases[78] $name ($username) $$phrases[79]:&nbsp; \n",
                $$page->password_field(-name           => "second_new_password",
                                       -size           => 32,
                                       -default        => "",
                                       -override       => 1,
                                       -maxlength      => 32));
print $$page->hidden(-name	=> "username",
                     -default	=> $username);
print $$page->hidden(-name	=> "name",
                     -default	=> $name);
print $$page->p(submit_button($page),cancel_button($page),
                main_menu_button($page));
print $$page->end_form();

print $$page->p({-class => "password-change-explanation"},
                $$phrases[80]);
print $$page->ul($$page->li({-class => "password-change-explanation"},
                            [
                             "$$phrases[81] $min_password_length $$phrases[82]",
                             $$phrases[83],
                             $$phrases[84]
                            ]
                           )
                );

return 1;

}

#-----------------------------------------------------------------

sub passwords_match {

my $page = $_[0];
my $first_new_password = $$page->param('first_new_password');
my $second_new_password = $$page->param('second_new_password');
my (@array_to_return,$md5_obj,$first_md5,$second_md5);
local $_;

$first_new_password =~ s/\s//go;
$second_new_password =~ s/\s//go;

if($first_new_password eq $second_new_password)
{
  $md5_obj = Digest::MD5->new;
  $md5_obj->add($first_new_password);
  $first_md5 = $md5_obj->hexdigest();
  $md5_obj = '';
  $md5_obj = Digest::MD5->new;
  $md5_obj->add($second_new_password);
  $second_md5 = $md5_obj->hexdigest();
  if($first_md5 eq $second_md5)
  {
    @array_to_return = (1,$first_md5);
  }
  else
  {
    @array_to_return = (0);
  }
}
else
{
  @array_to_return = (0);
}

return(\@array_to_return);

}
  
#-----------------------------------------------------------------

sub change_password_in_db {

my $page = $_[0];
my $pwd_hash = $_[1];
my $user_id = $$page->cookie($id_cookie);
my ($ok,$sql_prepared);
local $_;

$sql_prepared = "update recipe_users set password = ? where id = ?";
my $sth = $dbh->prepare($sql_prepared);
$ok = $sth->execute($pwd_hash,$user_id);

if(!$ok)
{
  die("Could not update password for user_id \"$user_id\" in db:  $!\n");
}
else
{
  return 1;
}

}

#-----------------------------------------------------------------

sub print_successful_password_change {

my $page = $_[0];
my $user_id = $$page->cookie($id_cookie);
my $username = $$page->param('username');
my $name = $$page->param('name');
local $_;

print_start_form($page,$cgi_name);

print $$page->p("$$phrases[85] $name ($username) $$phrases[86]");

print $$page->p(main_menu_button($page));
print $$page->end_form();
return 1;

}

#-----------------------------------------------------------------

sub print_password_unchanged {

my $page = $_[0];
local $_;

print $$page->p($$phrases[87]);

print_start_form($page,$cgi_name);
print $$page->p(main_menu_button($page));
print $$page->end_form();
return 1;

}


#-----------------------------------------------------------------

sub password_valid {

my (%password_checks,@error_array,$success);
local $_;

$success = 1;

foreach(@_)
{
  s/\s//go;
  if(length() >= $min_password_length)
  {
    $password_checks{$_} = [1];
  }
  else
  {
    $password_checks{$_} = [0];
  }
  if((/\d/o) && (/[a-zA-Z]/o))
  {
    $password_checks{$_}[1] = 1;
  }
  else
  {
    $password_checks{$_}[1] = 0;
  }
}

foreach(@_)
{
  if($password_checks{$_}[0])
  {
    $error_array[0] = -1;
  }
  else
  {
    $error_array[0] = 2;
    $success = 0;
  }
  if($password_checks{$_}[1])
  {
    $error_array[1] = -1;
  }
  else
  {
    $error_array[1] = 3;
    $success = 0;
  }
}

return([$success,\@error_array]);

}

#-----------------------------------------------------------------

my $submit_value = 0;

connect_to_db();

if(verify_session_id(\$page))
{
  print_page_header(\$page);
  print_title(\$page);
  my $submit_value = 0;
  if(defined($page->param('buttons')))
  {
    $submit_value = $page->param('buttons');
  }
  if(($submit_value) && ($submit_value eq $$phrases[70]))
  { 
    my $valid_checks = password_valid($page->param('first_new_password'),$page->param('second_new_password'));
    if($$valid_checks[0])
    {
      my $password_match_and_hash = passwords_match(\$page);
      if($$password_match_and_hash[0])
      {
        if(change_password_in_db(\$page,$$password_match_and_hash[1]))
        {
          print_successful_password_change(\$page);
        }
      }
      else
      {
        print_change_form(\$page,[1]);
      }
    }
    else
    {
      print_change_form(\$page,$$valid_checks[1]);
    }
  }
  elsif(($submit_value) && ($submit_value eq $$phrases[88]))
  { 
    print_password_unchanged(\$page);
  }
  else
  { 
    print_change_form(\$page,0);
  }
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
