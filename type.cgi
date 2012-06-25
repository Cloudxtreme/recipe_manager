#!/usr/bin/perl -wT

use lib ".";
use strict;
use CGI qw/:standard *table/;
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

print $$page->h2({-class => 'title'},$type_title);

return 1;

}

#-----------------------------------------------------------------

sub print_buttons {

my $page = $_[0];
local $_;

print $$page->p(add_button($page),edit_button($page),delete_button($page),
                  reset_button($page),main_menu_button($page));

}

#-----------------------------------------------------------------

sub print_record {

my ($page,$button,$class_key) = @_;
my $class = 'even-lines';
local $_;

unless($class_key)
{
  $class = 'odd-lines';
}

print $$page->Tr({-class => $class},$$page->td($$button));

return 1;

}

#-----------------------------------------------------------------

sub build_data_structures {

my ($sth,@id_array,%value_hash,$results,$id,$value);
local $_;

$sth = perform_search();

while((($id,$value) = $sth->fetchrow_array()))
{
  push(@id_array,$id);
  $value_hash{$id} = $value;
}

$sth->finish();

return(\@id_array,\%value_hash);

}

#-----------------------------------------------------------------


sub perform_search {

my ($sth,$sql);
local $_;

$sql = "select * from food_type order by name";
$sth = $dbh->prepare($sql);
$sth->execute();

return ($sth);

}

#-----------------------------------------------------------------

sub print_no_records_found {

my $page = $_[0];

print $$page->p($$phrases[86]);

print_start_form($page,$cgi_name);

print $$page->p({-align => "center"},add_button($page),main_menu_button($page));

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub print_all_types {

my $page = $_[0];
my $type_select_error_found = $_[1];
my ($id_array,$value_hash,$class_key,@radio_array);
local $_;

($id_array,$value_hash) = build_data_structures();

if(!(@$id_array))
{
  print_no_records_found($page);
  return 1;
}
else
{
  if($type_select_error_found)
  {
    print $$page->p({-class => 'brightred'},$$phrases[55]);
  }
  print_start_form($page,$cgi_name);

  print_buttons($page);

  print $$page->start_table({-cellpadding       => 3,
                             -cellspacing       => 3,
                             -border            => 0,
                             -width             => "100%"});

  @radio_array = $$page->radio_group(-name => 'type_id',
                                     -values => $id_array,
                                     -default => '-',
                                     -labels => $value_hash);

  $class_key = 1;

  foreach(@radio_array)
  {
      $class_key = $class_key ? 0 : 1;
      print_record($page,\$_,$class_key);
  }

  print $$page->end_table();

  print_buttons($page);

  print $$page->end_form();
}

return 1;

}

#-----------------------------------------------------------------

sub print_insertion_form {

my $page = $_[0];
local $_;

print_start_form($page,$cgi_name);

print $$page->p($$phrases[91]);

print $$page->textfield(-name		=> 'type_to_add',
                        -size		=> 80,
                        -default	=> '',
                        -maxlength	=> 128);
print $$page->p(add_button($page),reset_button($page),menu_button($page),
                main_menu_button($page));

print $$page->end_form();               

return 1;

}

#-----------------------------------------------------------------

sub insert_type_into_db {

my $type = $_[0];
my ($ok,$sql,$sth);
local $_;

$sql = "insert food_type (name) values (?)";
$sth = $dbh->prepare($sql);     
$ok = $sth->execute($type);

unless($ok)
{
  die("There was an error inserting a type into the db:  $!\n");
}     

return 1;

}

#-----------------------------------------------------------------

sub print_successful_insertion {

my $page = $_[0];
my $type = $$page->param('type_to_add');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);

print $$page->p($$page->b({-class => 'royalblue'},$type),
                $$phrases[57]);
print $$page->p([$$phrases[91],$$phrases[92],$$phrases[59]]);
print $$page->p(add_button($page),menu_button($page),main_menu_button($page));
print $$page->end_form();
return 1;

}

#-----------------------------------------------------------------

sub print_successful_edit {

my $page = $_[0];
my $new_type_name = $$page->param('new_type_name');
my $old_type_name = $$page->param('old_type_name');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);

$old_type_name = CGI->escapeHTML($old_type_name);
$new_type_name = CGI->escapeHTML($new_type_name);

print $$page->p($$page->b({-class => 'royalblue'},$old_type_name),
                $$phrases[60],$$page->b({-class => 'royalblue'},
                $new_type_name));
print $$page->p([$$phrases[92],$$phrases[59]]);
print $$page->p(menu_button($page),main_menu_button($page));
print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub show_edit_page {

my $page = $_[0];
my $type_id = $_[1];
my ($sth,$name,$sql);
local $_;

print $$page->p([$$phrases[62],$$phrases[63],$$phrases[64],$$phrases[93],
                 $$phrases[66]]);

$sql = "select name from food_type where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($type_id);

$name = $sth->fetchrow_array();

if(defined($name))
{
  print_start_form($page,$cgi_name);

  print $$page->textfield(-name           => "new_type_name",
                          -size           => 80,
                          -default        => $name,
                          -maxlength      => 128);
  print $$page->hidden(-name	=> "type_id",
                       -default	=> $type_id);
  print $$page->hidden(-name	=> "old_type_name",
                       -default => $name);
  print $$page->hidden(-name	=> "type_edited",
                       -default => "1");
  print $$page->p(save_button($page),reset_button($page),menu_button($page),
                  main_menu_button($page));
  print $$page->end_form();
  $sth->finish();
}
else
{
  die("Tried to edit type $type_id but it was not returned by the database:  $!\n");
}

return 1;
                            
}                                                                                                    

#-----------------------------------------------------------------

sub update_type_record_in_db {

my $type_id = $_[0];
my $new_type_name = $_[1];
my ($ok,$sql,$sth);
local $_;

$sql = "update food_type set name = ? where id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($new_type_name,$type_id);

if(!$ok)
{
  die("Updating type $type_id with \"$new_type_name\" failed:  $!\n");
}
else
{
  return 1;
}

}

#-----------------------------------------------------------------

sub print_successful_delete {

my $page = $_[0];
my $old_type_name = $$page->param('old_type_name');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);
$old_type_name = CGI->escapeHTML($old_type_name);

print $$page->p($$page->b({-class => 'royalblue'},$old_type_name),
                $$phrases[35]);
print $$page->p($$phrases[92],$$phrases[59]);
print $$page->p(menu_button($page),main_menu_button($page));
print $$page->end_form();
return 1;

}

#-----------------------------------------------------------------

sub delete_type_record_in_db {

my $type_id = $_[0];
my ($ok,$sql,$sth);
local $_;

$sql = "delete from food_type where id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($type_id);

if(!$ok)
{
  die("Deleting type $type_id failed:  $!\n");
}
else
{
  return 1;
}

}

#-----------------------------------------------------------------

sub show_delete_confirm_page {

my $page = $_[0];
my $type_id = $_[1];
my ($sth,$name,$sql);
local $_;

print $$page->p([$$phrases[67],$$phrases[68],$$phrases[94],$$phrases[66]]);


$sql = "select name from food_type where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($type_id);

$name = $sth->fetchrow_array();

if(defined($name))
{
  print_start_form($page,$cgi_name);

  print $$page->p({-class => "delete-confirm"},$$phrases[27],$name,
                  $$phrases[28]);
  print $$page->radio_group(-name       => "type_confirmed",
                            -values	=> [$$phrases[29],$$phrases[30]],
                            -default    => $$phrases[30],
                            -linebreak 	=> 'true');
  print $$page->hidden(-name	=> "type_id",
                       -default	=> $type_id);
  print $$page->hidden(-name	=> "old_type_name",
                       -default => $name);
  print $$page->p(submit_button($page),main_menu_button($page));

  print $$page->end_form();
  $sth->finish();
}
else
{
  die("Tried to confirm deletion of type $type_id but it was not returned by the database:  $!\n");
}

return 1;
                            
}                                                                                                    

#-----------------------------------------------------------------

sub print_no_delete {

my $page = $_[0];
my $old_type_name = $$page->param('old_type_name');
my $quote_prepared;
local $_;

$old_type_name = CGI->escapeHTML($old_type_name);

print $$page->p($$phrases[33],$$page->b({-class => 'royalblue'},
                $old_type_name),$$phrases[34]);

print_start_form($page,$cgi_name);
print $$page->p([$$phrases[92],$$phrases[59]]);
print $$page->p(menu_button($page),main_menu_button($page));
print $$page->end_form();
return 1;

}


#-----------------------------------------------------------------

my $button_value = 0;

connect_to_db();

if(verify_session_id(\$page))
{
  print_page_header(\$page);
  if(defined($page->param('buttons')))
  {
    $button_value = $page->param('buttons');
  }
  if($button_value eq $$phrases[72])
  {
    $button_value = $$phrases[52];
  }
  elsif($button_value eq $$phrases[70])
  {
    $button_value = $$phrases[53];
  }
  print_title(\$page);
  if(($button_value) && ($button_value eq $$phrases[71]))
  {
    my $type_to_add = 0;
    if(defined($page->param('type_to_add')))
    {
      $type_to_add = $page->param('type_to_add');
    }
    if($type_to_add)
    {
      if(insert_type_into_db($page->param('type_to_add')))
      {
        print_successful_insertion(\$page);
      }
    }
    else
    {
      print_insertion_form(\$page);
    }
  }
  elsif(($button_value) && ($button_value eq $$phrases[52]))
  {
    my $type_to_edit = 0;
    my $type_edited = 0;
    my $new_type_name = "";
    if(defined($page->param('type_id')))
    {
      $type_to_edit = $page->param('type_id');
    }
    if(defined($page->param('type_edited')))
    {
      $type_edited = $page->param('type_edited');
      $new_type_name = $page->param('new_type_name');
    }
    if(($type_to_edit) && ($type_edited))
    {
      if(update_type_record_in_db($type_to_edit,$new_type_name))
      {
        print_successful_edit(\$page);
      }
    }
    elsif($type_to_edit)
    {
      show_edit_page(\$page,$type_to_edit);
    }
    else
    {
      print_all_types(\$page,1);
    }
  }
  elsif(($button_value) && ($button_value eq $$phrases[53]))
  {
    my $type_to_delete = 0;
    my $type_confirmed = 0;
    if(defined($page->param('type_id')))
    {
      $type_to_delete = $page->param('type_id');
    }
    if(defined($page->param('type_confirmed')))
    {
      $type_confirmed = $page->param('type_confirmed');
    }
    if(($type_to_delete) && ($type_confirmed eq $$phrases[29]))
    {
      if(delete_type_record_in_db($type_to_delete))
      {
        print_successful_delete(\$page);
      }
    }
    elsif(($type_to_delete) && ($type_confirmed eq $$phrases[30]))
    {
      print_no_delete(\$page);
    }
    elsif($type_to_delete)
    {
      show_delete_confirm_page(\$page,$type_to_delete);
    }
    else
    {
      print_all_types(\$page,1);
    }
  }
  else
  {
    print_all_types(\$page,0);
  }
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
