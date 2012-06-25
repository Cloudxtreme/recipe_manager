#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser set_message);
use XML::Simple;
use RecipeManager;
use DBI;
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

#-----------------------------------------------------------------

sub print_menu_page {

my $page = $_[0];
local $_;

print $$page->h1({-class => "main-title"},$main_menu_title);
print $$page->table({-border		=> 0,
                     -cellpadding	=> 3,
                     -cellspacking	=> 3,
                     -width		=> "100%",
                     -align		=> "center"},
                    $$page->Tr({-class => "menu-lines"},
                              [
                              $$page->td(
                                        [
                                          $$page->a({-href=>"http://$add_cgi",
                                                     -class=>"plain"},
                                                    "$add_title"),
                                          $$page->a({-href=>"http://$browse_cgi",
                                                     -class=>"plain"},
                                                    "$browse_title"),
                                        ]),
                              $$page->td({-colspan => 2},
#                                         [
                                          $$page->a({-href=>"http://$search_cgi",
                                                     -class=>"plain"},
                                                    "$search_title"),
#                                          $$page->a({-href=>"http://$browse_cgi",
#                                                     -class=>"plain"},
#                                                   "$browse_title"),
#                                         ]
                                        ),
                              $$page->td(
                                        [
                                          $$page->a({-href=>"http://$type_cgi",
                                                     -class=>"plain"},
                                                    "$type_title"),
                                          $$page->a({-href=>"http://$origin_cgi",
                                                     -class=>"plain"},
                                                    "$origin_title"),
                                        ]),
                              $$page->td(
                                         [
                                          $$page->a({-href=>"http://$password_cgi",
                                                     -class=>"plain"},
                                                    "$password_title"),
                                          $$page->a({-href=>"http://$logout_cgi",
                                                     -class=>"plain"},
                                                    "$logout_title"),
                                         ]
                                        ),
                                        
                              ])
                   );
                

}

#-----------------------------------------------------------------

my $page = new CGI;

connect_to_db();

if(verify_session_id(\$page))
{
  print_page_header(\$page);
  print_menu_page(\$page);
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();

