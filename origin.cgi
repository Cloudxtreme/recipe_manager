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

print $$page->h2({-class => 'title'},$origin_title);

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

$sql = "select * from original_source order by name";
$sth = $dbh->prepare($sql);
$sth->execute();

return ($sth);

}

#-----------------------------------------------------------------

sub print_no_records_found {

my $page = $_[0];

print $$page->p($$phrases[54]);

print_start_form($page,$cgi_name);

print $$page->p({-align => "center"},add_button($page),main_menu_button($page));

print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub print_all_origins {

my $page = $_[0];
my $origin_select_error_found = $_[1];
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
  if($origin_select_error_found)
  {
    print $$page->p({-class => 'brightred'},$$phrases[55]);
  }
  print_start_form($page,$cgi_name);

  print_buttons($page);

  print $$page->start_table({-cellpadding       => 3,
                             -cellspacing       => 3,
                             -border            => 0,
                             -width             => "100%"});

  @radio_array = $$page->radio_group(-name => 'origin_id',
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

print $$page->p($$phrases[56]);

print $$page->textfield(-name		=> 'origin_to_add',
                        -size		=> 80,
                        -default	=> '',
                        -maxlength	=> 128);
print $$page->p(add_button($page),reset_button($page),menu_button($page),
                main_menu_button($page));

print $$page->end_form();               

return 1;

}

#-----------------------------------------------------------------

sub insert_origin_into_db {

my $origin = $_[0];
my ($ok,$sql,$sth);
local $_;

$sql = "insert original_source (name) values (?)";
$sth = $dbh->prepare($sql);     
$ok = $sth->execute($origin);

unless($ok)
{
  die("There was an error inserting a origin into the db:  $!\n");
}     

return 1;

}

#-----------------------------------------------------------------

sub print_successful_insertion {

my $page = $_[0];
my $origin = $$page->param('origin_to_add');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);

print $$page->p($$page->b({-class => 'royalblue'},$origin),
                $$phrases[57]);
print $$page->p([$$phrases[58],$$phrases[61],$$phrases[59]]);
print $$page->p(add_button($page),menu_button($page),main_menu_button($page));
print $$page->end_form();
return 1;

}

#-----------------------------------------------------------------

sub print_successful_edit {

my $page = $_[0];
my $new_origin_name = $$page->param('new_origin_name');
my $old_origin_name = $$page->param('old_origin_name');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);

$old_origin_name = CGI->escapeHTML($old_origin_name);
$new_origin_name = CGI->escapeHTML($new_origin_name);

print $$page->p($$page->b({-class => 'royalblue'},$old_origin_name),
                $$phrases[60],$$page->b({-class => 'royalblue'},
                $new_origin_name));
print $$page->p([$$phrases[61],$$phrases[59]]);
print $$page->p(menu_button($page),main_menu_button($page));
print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

sub show_edit_page {

my $page = $_[0];
my $origin_id = $_[1];
my ($sth,$name,$sql);
local $_;

print $$page->p([$$phrases[62],$$phrases[63],$$phrases[64],$$phrases[65],
                 $$phrases[66]]);

$sql = "select name from original_source where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($origin_id);

$name = $sth->fetchrow_array();

if(defined($name))
{
  print_start_form($page,$cgi_name);

  print $$page->textfield(-name           => "new_origin_name",
                          -size           => 80,
                          -default        => $name,
                          -maxlength      => 128);
  print $$page->hidden(-name	=> "origin_id",
                       -default	=> $origin_id);
  print $$page->hidden(-name	=> "old_origin_name",
                       -default => $name);
  print $$page->hidden(-name	=> "origin_edited",
                       -default => "1");
  print $$page->p(save_button($page),reset_button($page),menu_button($page),
                  main_menu_button($page));
  print $$page->end_form();
  $sth->finish();
}
else
{
  die("Tried to edit origin $origin_id but it was not returned by the database:  $!\n");
}

return 1;
                            
}                                                                                                    

#-----------------------------------------------------------------

sub update_origin_record_in_db {

my $origin_id = $_[0];
my $new_origin_name = $_[1];
my ($ok,$sql,$sth);
local $_;

$sql = "update original_source set name = ? where id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($new_origin_name,$origin_id);

if(!$ok)
{
  die("Updating origin $origin_id with \"$new_origin_name\" failed:  $!\n");
}
else
{
  return 1;
}

}

#-----------------------------------------------------------------

sub print_successful_delete {

my $page = $_[0];
my $old_origin_name = $$page->param('old_origin_name');
my $quote_prepared;
local $_;

print_start_form($page,$cgi_name);
$old_origin_name = CGI->escapeHTML($old_origin_name);

print $$page->p($$page->b({-class => 'royalblue'},$old_origin_name),
                $$phrases[35]);
print $$page->p($$phrases[61],$$phrases[59]);
print $$page->p(menu_button($page),main_menu_button($page));
print $$page->end_form();
return 1;

}

#-----------------------------------------------------------------

sub delete_origin_record_in_db {

my $origin_id = $_[0];
my ($ok,$sql,$sth);
local $_;

$sql = "delete from original_source where id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($origin_id);

if(!$ok)
{
  die("Deleting origin $origin_id failed:  $!\n");
}
else
{
  return 1;
}

}

#-----------------------------------------------------------------

sub show_delete_confirm_page {

my $page = $_[0];
my $origin_id = $_[1];
my ($sth,$name,$sql);
local $_;

print $$page->p([$$phrases[67],$$phrases[68],$$phrases[69],$$phrases[66]]);


$sql = "select name from original_source where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($origin_id);

$name = $sth->fetchrow_array();

if(defined($name))
{
  print_start_form($page,$cgi_name);

  print $$page->p({-class => "delete-confirm"},$$phrases[27],$name,
                  $$phrases[28]);
  print $$page->radio_group(-name       => "origin_confirmed",
                            -values	=> [$$phrases[29],$$phrases[30]],
                            -default    => $$phrases[30],
                            -linebreak 	=> 'true');
  print $$page->hidden(-name	=> "origin_id",
                       -default	=> $origin_id);
  print $$page->hidden(-name	=> "old_origin_name",
                       -default => $name);
  print $$page->p(submit_button($page),main_menu_button($page));

  print $$page->end_form();
  $sth->finish();
}
else
{
  die("Tried to confirm deletion of origin $origin_id but it was not returned by the database:  $!\n");
}

return 1;
                            
}                                                                                                    

#-----------------------------------------------------------------

sub print_no_delete {

my $page = $_[0];
my $old_origin_name = $$page->param('old_origin_name');
my $quote_prepared;
local $_;

$old_origin_name = CGI->escapeHTML($old_origin_name);

print $$page->p($$phrases[33],$$page->b({-class => 'royalblue'},
                $old_origin_name),$$phrases[34]);

print_start_form($page,$cgi_name);
print $$page->p([$$phrases[61],$$phrases[59]]);
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
    my $origin_to_add = 0;
    if(defined($page->param('origin_to_add')))
    {
      $origin_to_add = $page->param('origin_to_add');
    }
    if($origin_to_add)
    {
      if(insert_origin_into_db($page->param('origin_to_add')))
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
    my $origin_to_edit = 0;
    my $origin_edited = 0;
    my $new_origin_name = "";
    if(defined($page->param('origin_id')))
    {
      $origin_to_edit = $page->param('origin_id');
    }
    if(defined($page->param('origin_edited')))
    {
      $origin_edited = $page->param('origin_edited');
      $new_origin_name = $page->param('new_origin_name');
    }
    if(($origin_to_edit) && ($origin_edited))
    {
      if(update_origin_record_in_db($origin_to_edit,$new_origin_name))
      {
        print_successful_edit(\$page);
      }
    }
    elsif($origin_to_edit)
    {
      show_edit_page(\$page,$origin_to_edit);
    }
    else
    {
      print_all_origins(\$page,1);
    }
  }
  elsif(($button_value) && ($button_value eq $$phrases[53]))
  {
    my $origin_to_delete = 0;
    my $origin_confirmed = 0;
    if(defined($page->param('origin_id')))
    {
      $origin_to_delete = $page->param('origin_id');
    }
    if(defined($page->param('origin_confirmed')))
    {
      $origin_confirmed = $page->param('origin_confirmed');
    }
    if(($origin_to_delete) && ($origin_confirmed eq $$phrases[29]))
    {
      if(delete_origin_record_in_db($origin_to_delete))
      {
        print_successful_delete(\$page);
      }
    }
    elsif(($origin_to_delete) && ($origin_confirmed eq $$phrases[30]))
    {
      print_no_delete(\$page);
    }
    elsif($origin_to_delete)
    {
      show_delete_confirm_page(\$page,$origin_to_delete);
    }
    else
    {
      print_all_origins(\$page,1);
    }
  }
  else
  {
    print_all_origins(\$page,0);
  }
  print $page->end_html();
}
else
{
  print_session_expired_page(\$page);
}

disconnect_from_db();
