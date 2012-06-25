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
my $cgi_name = $page->url();

#-----------------------------------------------------------------

sub print_title {

my $page = $_[0];
local $_;

print $$page->h2({-class => 'title'},$view_title);

return 1;

}

#-----------------------------------------------------------------

sub print_recipe {

my $page = $_[0];
my $recipe_id = $_[1];
my ($sth,$results,$id,$name,$class_key,$food_name,$field,
    $field_name,$field_info,$field_type,@table_rows,$label,$data,
    $early_data,$sql);
local $_;

$sql = "select *  from recipes where id = ?";
$sth = $dbh->prepare($sql);
$sth->execute($recipe_id);

$results = $sth->fetchrow_hashref();

foreach $field (@$form_field_order)
{
  $field_info = $$form_field_hash{$field};
  $field_name = $field;
  $field_type = $field_info->{'type'};
  unless($field_name eq "name")
  {
    $label = $$page->span({-style => "text-align: right; font-weight: bold"}, CGI->escapeHTML($field_info->{'label'}));
  }

  if($field_type eq "function")
  {
    $early_data = CGI->escapeHTML($form_field_functions{$field_info->{'view_function'}}->($results->{$field}));
    unless($early_data) { $early_data = "&nbsp;"; }
    $data = $$page->span({-right => "text-align: left"}, $early_data);
  }
  else
  {
    if(defined($results->{$field_name}))
    { 
      $early_data = CGI->escapeHTML($results->{$field_name});
      $early_data =~ s/\r\n/\<br\ \/\>/go;
      if($field_name eq "name")
      {
        $data = $$page->h3({-class => "recipe-title"},$early_data);
      }
      else
      {
        $data = $$page->span({-style => "text-align: left"},$early_data);
      }
    }
    else
    {
      $data = $$page->span({-style => "text-align: left"}, "I'm a placeholder.\n");
    }
  }
  if($field_name eq "name")
  {
    push(@table_rows,$$page->td({-colspan => 2},$data));
  }
  else
  {
    push(@table_rows,$$page->td({-style => "vertical-align: top"},[$label,$data]));
  }
}

print $$page->table({-cellpadding	=> "3",
                     -border		=> "0",
                     -width		=> "100%",
                     -align		=> "center"},
                     $$page->Tr(\@table_rows));

$sth->finish();

print_start_form($page,$cgi_name);

print $$page->p(back_js_button($page),edit_js_button($page),delete_js_button($page),
                main_menu_button($page));
                
if(defined($$page->param('search_defined')))
{
  include_back_to_search($page);
}
print $$page->hidden(-name	=> "recipe_id",
                     -default	=> $recipe_id);
print $$page->end_form();

return 1;

}

#-----------------------------------------------------------------

my $recipe_id = 0;
my $search_string = "";

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
  if($recipe_id)
  {
    if(defined($page->param('search_string')))
    {
      $search_string = $page->param('search_string');
    }
    elsif(defined($page->url_param('search_string')))
    {
      $search_string = $page->url_param('search_string');
    }
    if($search_string)
    {
      print_page_header(\$page,0,1,$recipe_id,$search_string);
    }
    else
    {
      print_page_header(\$page,0,1,$recipe_id);
    }
    print_title(\$page);
    print_recipe(\$page,$recipe_id);
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

disconnect_from_db();
