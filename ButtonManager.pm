package 	ButtonManager;
#require 	Exporter;
use		AutoLoader 'AUTOLOAD';
#
# AutoSplit with
# perl -e 'use AutoSplit; autosplit($ARGV[0], $ARGV[1], 0, 1, 1)' ButtonManager.pm auto
#
our @ISA	= qw(Exporter);
our @EXPORT	= qw(back_js_button main_menu_button save_button reset_button 
                     cancel_button add_button edit_button delete_button 
                     submit_button menu_button login_button add_js_button 
                     view_button new_search_button search_button setup_buttons
                     edit_js_button delete_js_button
		    );
our @EXPORT_OK	= qw();
our $VERSION	= 0.9;

use strict;

our ($back_js_title,$main_menu_title,$save_title,$reset_title,$cancel_title,
     $add_title,$edit_title,$delete_title,$submit_title,$menu_title,
     $login_title,$add_js_title,$view_title,$new_search_title,$search_title
    );

$XML::Simple::PREFERRED_PARSER='XML::SAX::Expat';

#####################################################################

1;

__END__

#--------------------------------------------------------------------

sub setup_buttons {

my $config_file = "/home/dbogen/userland/projects/recipes/button-config.xml";
my $config;
my $xml_obj = new XML::Simple;
local $_;

$config = $xml_obj->XMLin($config_file,
                          NormalizeSpace => 2);
#use Data::Dumper;
#print STDERR Dumper($config);

$back_js_title = $config->{'buttons'}->{'back_js'};
$main_menu_title = $config->{'buttons'}->{'main_menu'};
$save_title = $config->{'buttons'}->{'save'};
$reset_title = $config->{'buttons'}->{'reset'};
$cancel_title = $config->{'buttons'}->{'cancel'};
$add_title = $config->{'buttons'}->{'add'};
$edit_title = $config->{'buttons'}->{'edit'};
$delete_title = $config->{'buttons'}->{'delete'};
$submit_title = $config->{'buttons'}->{'submit'};
$menu_title = $config->{'buttons'}->{'menu'};
$login_title = $config->{'buttons'}->{'login'};
$add_js_title = $config->{'buttons'}->{'add_js'};
$view_title = $config->{'buttons'}->{'view'};
$new_search_title = $config->{'buttons'}->{'new_search'};
$search_title = $config->{'buttons'}->{'search'};

return 1;

}

#--------------------------------------------------------------------

sub save_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                      -value   => $save_title));
}                     

#--------------------------------------------------------------------

sub reset_button {

my $page = $_[0];
local $_;

return($$page->reset(-name    => 'reset',
                     -value   => $reset_title));
}                     

#--------------------------------------------------------------------

sub cancel_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $cancel_title));
}                     

#--------------------------------------------------------------------

sub main_menu_button {

my $page = $_[0];
local $_;

return($$page->button(-name    => 'MainMenuButton',
                     -value   => $main_menu_title,
                     -onClick => 'MainMenu()'));
}                     

#--------------------------------------------------------------------

sub add_js_button {

my $page = $_[0];
local $_;

return($$page->button(-name    => 'AddButton',
                     -value   => $add_js_title,
                     -onClick => 'AddRecipe()'));
}                     

#--------------------------------------------------------------------

sub edit_js_button {

my $page = $_[0];
local $_;

return($$page->button(-name    => 'EditButton',
                     -value   => $edit_title,
                     -onClick => 'EditID()'));
}                     

#--------------------------------------------------------------------
sub delete_js_button {

my $page = $_[0];
local $_;

return($$page->button(-name    => 'DeleteButton',
                     -value   => $delete_title,
                     -onClick => 'DeleteID()'));
}                     

#--------------------------------------------------------------------

sub add_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $add_title));
}                     

#--------------------------------------------------------------------

sub edit_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $edit_title));
}                     

#--------------------------------------------------------------------

sub delete_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $delete_title));
}                     

#--------------------------------------------------------------------

sub submit_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $submit_title));
}                     

#--------------------------------------------------------------------

sub menu_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $menu_title));
}                     

#--------------------------------------------------------------------

sub login_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $login_title));
}                     

#--------------------------------------------------------------------

sub view_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $view_title));
}                     

#--------------------------------------------------------------------

sub new_search_button {

my $page = $_[0];
local $_;

return($$page->button(-name => "NewSearch",
                      -value => $new_search_title,
                      -onclick => "SearchRecipes()"));
}                     

#--------------------------------------------------------------------

sub back_js_button {

my $page = $_[0];
local $_;

return($$page->button(-name => "GoBack",
                      -value => $back_js_title,
                      -onclick => 'history.go(-1)'));
}                     

#--------------------------------------------------------------------

sub search_button {

my $page = $_[0];
local $_;

return($$page->submit(-name    => 'buttons',
                     -value   => $search_title));
}                     

#--------------------------------------------------------------------

1;
