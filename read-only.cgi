#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI;
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

sub get_locked_by_name {

my $recipe_id = $_[0];
my ($sth,$ok,$user_id,$sql,$name);
local $_;

$sql = 'select locked_by from recipes where id = ?';
$sth = $dbh->prepare($sql);
$sth->execute($recipe_id);

($user_id) = $sth->fetchrow_array();

unless($user_id)
{
  die("Ack!  Record $recipe_id is locked with no locked_by value:  $!\n");
}

$name = reverse_user_id($user_id);

return($name);

}

#-----------------------------------------------------------------

sub print_read_only_page {

my $page = $_[0];
my $locked_by_name = get_locked_by_name($$page->param('recipe_id'));
local $_;

print $$page->h2({-class => 'title'},$read_only_title);

print_start_form($page,$cgi_name);

print $$page->p(["$$phrases[24] ${locked_by_name}.",$$phrases[25],$$phrases[23]]);

print $$page->p(back_js_button($page),view_button($page),main_menu_button($page));

if(defined($$page->url_param('search_defined')))
{
  include_back_to_search($page);
}

include_hidden_fields($page);

print $$page->end_form();
                

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

if(defined($$page->url_param('display_all_records')))
{
  print $$page->hidden(-name    => 'display_all_records',
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

my $button_value = '';

connect_to_db();

if(verify_session_id(\$page))
{
  if(defined($page->param('buttons')))
  {
    $button_value = $page->param('buttons');
  }
  if(($button_value) && ($button_value eq $$phrases[20]))
  {
    redirect_to_view(\$page);
  }
  else
  {
    print_page_header(\$page);
    print_read_only_page(\$page);
    print $page->end_html();
  }
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
