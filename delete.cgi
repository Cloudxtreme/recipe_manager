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
my $cgi_name = $page->url(-query => 1);

#-----------------------------------------------------------------

sub print_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$delete_title);

return 1;

}

#-----------------------------------------------------------------

sub print_confirm_delete {

my $page = $_[0];
my $recipe_id = $_[1];
my ($sth,$recipe_title,@results,$quote_prepared,$sql);
local $_;

print $$page->p($$phrases[26]);
$sql = "select name from recipes where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($recipe_id);

@results = $sth->fetchrow_array();

$recipe_title = $results[0];

$sth->finish();

print_start_form($page,$cgi_name);

print $$page->hidden(-name    => "recipe_name",
                     -default => $recipe_title);
                     
$recipe_title = CGI->escapeHTML($recipe_title);

print $$page->p({-class => "delete-confirm"},"$$phrases[27] $recipe_title
                                              $$phrases[28]");
print $$page->radio_group(-name       => "delete_confirmed",
                          -values     => [$$phrases[29],$$phrases[30]],
                          -default    => $$phrases[30],
                          -linebreak  => 'true');
print $$page->hidden(-name    => "recipe_id",
                     -default => $recipe_id);
print $$page->hidden(-name    => "delete_confirm_shown",
                     -default => 1);
print $$page->p(submit_button($page));
print $$page->hidden(-name	=> "recipe_id",
                     -default	=> $recipe_id);
print $$page->end_form();

print $$page->p([$$phrases[31],$$phrases[32]]);

return 1;

}

#-----------------------------------------------------------------

sub print_delete_cancelled {

my $page = $_[0];
my $recipe_name = $$page->param('recipe_name');
local $_;

$recipe_name = CGI->escapeHTML($recipe_name);

print $$page->p($$phrases[33],$$page->b({-class => 'royalblue'},$recipe_name),
                $$phrases[34]);

print_start_form($page,$cgi_name);

print $$page->p(main_menu_button($page));

if((defined($$page->param('search_defined'))) ||
   (defined($$page->url_param('search_defined'))))
{
  include_back_to_search($page);
}

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub show_delete_completed {

my $page = $_[0];
my $recipe_name = $$page->param('recipe_name');
local $_;

$recipe_name = CGI->escapeHTML($recipe_name);

print $$page->p($$page->b({-class => 'royalblue'},$recipe_name),$$phrases[35]);

print_start_form($page,$cgi_name);

print $$page->p(main_menu_button($page));

if((defined($$page->param('search_defined'))) ||
   (defined($$page->url_param('search_defined'))))
{
  include_back_to_search($page);
}
print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub delete_recipe {

my $recipe_id = $_[0];
my ($ok,$sql,$sth);
local $_;

$sql = "delete from recipes where id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($recipe_id);

if(!$ok)
{
  die("Could not delete from recipes table where id = $recipe_id:  $!\n");
}

return 1;

}

#-----------------------------------------------------------------

my $recipe_id = 0;
my $delete_confirm_shown = 0;
my $delete_confirm = 0;

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
  if(defined($page->param('delete_confirm_shown')))
  {
    $delete_confirm_shown = $page->param('delete_confirm_shown');
  }
  if(defined($page->param('delete_confirmed')))
  {
    $delete_confirm = $page->param('delete_confirmed');
  }
  establish_lock(\$page,$recipe_id);
  if(($recipe_id) && ($delete_confirm_shown) && ($delete_confirm eq $$phrases[29]))
  {
    delete_recipe($recipe_id);
    print_page_header(\$page);
    print_title(\$page);
    show_delete_completed(\$page);
    print $page->end_html();
  }
  elsif(($recipe_id) && ($delete_confirm_shown) && ($delete_confirm eq $$phrases[30]))
  {
    release_lock($recipe_id);
    print_page_header(\$page);
    print_title(\$page);
    print_delete_cancelled(\$page);
    print $page->end_html();
  }
  elsif($recipe_id)
  {
    print_page_header(\$page);
    print_title(\$page);
    print_confirm_delete(\$page,$recipe_id);
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
