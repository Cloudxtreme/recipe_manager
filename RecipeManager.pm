package 	RecipeManager;
require 	Exporter;

our @ISA	= qw(Exporter);
our @EXPORT	= qw(verify_session_id $dbh connect_to_db $form_field_order
                     $type_title $origin_title $view_cgi $break_lock_cgi
                     print_page_header $form_field_hash brsrch_determine_record_locked
                     print_origins $menu_cgi print_types get_food_type
                     $origin_cgi $add_cgi $browse_cgi %form_field_functions
                     $type_cgi setup_values get_radio_values $view_title
                     $add_title $browse_title redirect_to_view $edit_title
                     $main_menu_title disconnect_from_db no_parameter_found
                     get_original_source $delete_title $delete_cgi $edit_cgi
		     redirect_to_delete redirect_to_edit $search_title
		     $search_cgi $search_results_cgi redirect_to_results
		     redirect_to_search include_back_to_search $auth_cgi
		     $number_of_rows_to_display ceil $login_title $session_timeout
		     $session_cookie $id_cookie print_start_form 
		     print_session_expired_page $expired_cgi $expired_title
		     $small_lock_image $small_break_lock_image
		     include_lock_explanation redirect_if_locked release_lock
                     establish_lock reverse_user_id this_user_allowed_to_break_lock
                     redirect_to_read_only $read_only_cgi $break_lock_title
                     $read_only_title remove_trailing_whitespace $logout_cgi
                     transform_search_string reverse_search_string_transform
                     $logout_title $min_password_length $password_cgi
                     $password_title
		    );
our @EXPORT_OK	= qw();
our $VERSION	= 0.8;

our ($menu_cgi,$type_cgi,$origin_cgi,$add_cgi,$browse_cgi,$view_title,
     $dbh,$type_title,$origin_title,$add_title,$browse_title,$edit_cgi,
     $main_menu_title,$form_field_hash,$delete_cgi,$expired_cgi,
     $form_field_order,%form_field_functions,$view_cgi,$delete_title,
     $edit_title,$search_title,$search_cgi,$search_results_cgi,
     $number_of_rows_to_display,$login_title,$min_password_length,$auth_cgi,
     $session_timeout,$session_cookie,$id_cookie,$expired_title, $logout_cgi,
     $small_lock_image,$small_break_lock_image,$break_lock_cgi, $logout_title,
     $read_only_cgi,$break_lock_title,$read_only_title,
     $password_cgi,$password_title);
my ($author_email,$host,$cgi_path,$page_title,$lock_timeout,
    $meta_hash,$not_logged_in_csscode,$logged_in_csscode,
    $dsn, $db_username, $db_password,$ip_array);

#--------------------------------------------------------------------

sub setup_values {

my $config_file = "/home/dbogen/userland/projects/recipes/config.xml";
my $config;
my $xml_obj = new XML::Simple;
local $_;

$config = $xml_obj->XMLin($config_file);

#use Data::Dumper;
#print STDERR Dumper($config);

$host = $config->{'host'}->{'hostname'};
$port = $config->{'host'}->{'port'};
if($port ne "80")
{
  $host = "$host:$port";
}
if($config->{'cgi_path'})
{
  $host .= "/$config->{'cgi_path'}";
}

$menu_cgi = "$host/$config->{'scripts'}->{'menu'}";
$add_cgi = "$host/$config->{'scripts'}->{'add'}";
$type_cgi = "$host/$config->{'scripts'}->{'type'}";
$origin_cgi = "$host/$config->{'scripts'}->{'origin'}";
$browse_cgi = "$host/$config->{'scripts'}->{'browse'}";
$view_cgi = "$host/$config->{'scripts'}->{'view'}";
$delete_cgi = "$host/$config->{'scripts'}->{'delete'}";
$edit_cgi = "$host/$config->{'scripts'}->{'edit'}";
$search_cgi = "$host/$config->{'scripts'}->{'search'}";
$search_results_cgi = "$host/$config->{'scripts'}->{'search_results'}";
$auth_cgi = "$host/$config->{'scripts'}->{'auth'}";
$expired_cgi = "$host/$config->{'scripts'}->{'expired'}";
$break_lock_cgi = "$host/$config->{'scripts'}->{'break_lock'}";
$read_only_cgi = "$host/$config->{'scripts'}->{'read_only'}";
$logout_cgi = "$host/$config->{'scripts'}->{'logout'}";
$password_cgi = "$host/$config->{'scripts'}->{'password'}";


$page_title = $config->{'titles'}->{'page'};
$type_title = $config->{'titles'}->{'type'};
$origin_title = $config->{'titles'}->{'origin'};
$add_title = $config->{'titles'}->{'add'};
$browse_title = $config->{'titles'}->{'browse'};
$main_menu_title = $config->{'titles'}->{'main_menu'};
$view_title = $config->{'titles'}->{'view'};
$delete_title = $config->{'titles'}->{'delete'};
$edit_title = $config->{'titles'}->{'edit'};
$search_title = $config->{'titles'}->{'search'};
$login_title = $config->{'titles'}->{'auth'};
$expired_title = $config->{'titles'}->{'expired'};
$break_lock_title = $config->{'titles'}->{'break_lock'};
$read_only_title = $config->{'titles'}->{'read_only'};
$logout_title = $config->{'titles'}->{'logout'};
$password_title = $config->{'titles'}->{'password'};

$author_email = $config->{'author'};

$small_lock_image = $config->{'images'}->{'small_lock'};
$small_break_lock_image = $config->{'images'}->{'small_break_lock'};

$session_timeout = $config->{'session'}->{'timeout'};

$id_cookie = $config->{'cookies'}->{'id_cookie'};
$session_cookie = $config->{'cookies'}->{'session_cookie'};

$min_password_length = $config->{'password'}->{'minimum_length'};

$meta_hash = get_page_meta_information($config);

$lock_timeout = $config->{'locks'}->{'timeout'};

$ip_array = $config->{'allowed_hosts'}->{'host'};

my $db_host = $config->{'database'}->{'host'};
my $db_name = $config->{'database'}->{'name'};
$dsn = "DBI:mysql:$db_name:$db_host";
$db_username = $config->{'database'}->{'username'};
$db_password = $config->{'database'}->{'password'};

$number_of_rows_to_display = $config->{'display'}->{'rows_to_display'};

$not_logged_in_csscode = $config->{'css'}->{'not_logged_in'};
$logged_in_csscode = $config->{'css'}->{'logged_in'};

$form_field_hash =  get_form_field_hash($config);
$form_field_order = $config->{'form_fields'}->{'order'}->{'field'};

%form_field_functions = ( "print_origins" => \&print_origins,
                          "print_types"   => \&print_types,
                          "get_food_type" => \&get_food_type,
                          "get_original_source" => \&get_original_source,
                          "print_edit_types" => \&print_edit_types,
                          "print_edit_origins" => \&print_edit_origins
                        ); 

}

#--------------------------------------------------------------------

sub get_radio_values {

my $field_info = $_[0];
my $search_flag = $_[1];
my (@values,%value_hash,$value,$xml_array);
local $_;

if($search_flag)
{
  push(@values,0);
  $value_hash{0} = "Not Applicable";
}

$xml_array = $field_info->{'radio_values'}->{'radio_value'};

foreach $value (@$xml_array)
{
  push(@values,$value->{'value'});
  $value_hash{$value->{'value'}} = $value->{'label'};
}

return([\@values,\%value_hash]);

}

#--------------------------------------------------------------------

sub get_form_field_hash {

my $config = $_[0];
my %field_hash_to_return;
local $_;

my $field_hash = $config->{'form_fields'}->{'field'};

foreach(keys(%$field_hash))
{
  $field_hash_to_return{$_} = $config->{'form_fields'}->{'field'}->{$_};
}

return(\%field_hash_to_return);

}

#--------------------------------------------------------------------

sub connect_to_db {

$dbh = DBI->connect($dsn, $db_username, $db_password, {RaiseError => 1});

}

#--------------------------------------------------------------------

sub disconnect_from_db {

$dbh->disconnect();

}

#--------------------------------------------------------------------

sub print_page_header {

my $page = $_[0];
my $not_logged_in_flag = $_[1];
my $view_flag = $_[2];
my $recipe_id = $_[3];
my $search_string = $_[4];
my $javascript;
local $_;


print $$page->header();

if($not_logged_in_flag)
{
  print $$page->start_html(-title => $page_title,
                           -author => $author_email,
                           -meta => $meta_hash,
                           -style => {-code=>$not_logged_in_csscode});
}
else
{
$javascript=<<ENDJSCRIPT;

function MainMenu() {
  window.location="http://$menu_cgi";
}

function AddRecipe() {
  window.location="http://$add_cgi";
}

function SearchRecipes() {
  window.location="http://$search_cgi";
}

ENDJSCRIPT

if(($view_flag) && ($search_string))
{
  my $additional_javascript =<<END_ADDJSCRIPT;

function EditID() {
  window.location="http://$edit_cgi?recipe_id=$recipe_id&search_defined=1&search_string=$search_string";
}

function DeleteID() {
  window.location="http://$delete_cgi?recipe_id=$recipe_id&search_defined=1&search_string=$search_string";
}
END_ADDJSCRIPT

  $javascript .= $additional_javascript;
}
elsif($view_flag)
{
  my $additional_javascript =<<END_ADDJSCRIPT;

function EditID() {
  window.location="http://$edit_cgi?recipe_id=$recipe_id";
}

function DeleteID() {
  window.location="http://$delete_cgi?recipe_id=$recipe_id";
}
END_ADDJSCRIPT

  $javascript .= $additional_javascript;
}


  print $$page->start_html(-title => $page_title,
                           -author => $author_email,
                           -meta => $meta_hash,
                           -style => {-code=>$logged_in_csscode},
                           -script => $javascript);
}

}

#--------------------------------------------------------------------

sub update_session_timestamp_in_db {

my $session_id = $_[0];
my $session_timestamp = $_[1];
my($sth,$ok,$sql);
local $_;

$sql = "update recipe_sessions set session_time = ? where ".
       "session_id = ?";
$sth = $dbh->prepare($sql);
$ok = $sth->execute($session_timestamp,$session_id);

if(!$ok)
{
  die("Updating $session_id in update_session_timestamp_in_db failed:  $!\n");
}
else
{
  return 1;
}

}

#--------------------------------------------------------------------

sub verify_session_id {

my $page = $_[0];
my $current_time = time();
my($sth,$results,$session_id,$sql);
local $_;

if(defined($$page->cookie($session_cookie)))
{
  $session_id = $$page->cookie($session_cookie);
}
else
{
  $session_id = 0;
}

$sql = 'select session_time from recipe_sessions where session_id = ?';
$sth = $dbh->prepare($sql);
$sth->execute($session_id);
$results = $sth->fetchrow_hashref();

if($results->{'session_time'})
{
  if(($current_time - $session_timeout) <= $results->{'session_time'})
  {
    update_session_timestamp_in_db($session_id,$current_time);
    $sth->finish();
    return 1;
  }
  else
  {
    $sth->finish();
    return 0;
  }
}
else
{
  $sth->finish();
  return 0;
}

}

#--------------------------------------------------------------------

sub get_page_meta_information {

my $config = $_[0];
my (%meta_info,$hash);
local $_;

$hash = $config->{'meta'}->{'tag'};

foreach(keys(%$hash))
{
  $meta_info{$_} = $config->{'meta'}->{'tag'}->{$_}->{'content'};
}

return(\%meta_info);

}

#--------------------------------------------------------------------

sub compile_types {

my ($sth, $id, $name, @values_array, @labels_hash, @array_to_return);
local $_;

push(@values_array,0);
$labels_hash{"0"} = "Not Applicable";

$sth = $dbh->prepare("select id,name from food_type order by name");
$sth->execute();

while(($id,$name) = $sth->fetchrow_array())
{
  push(@values_array,$id);
  $labels_hash{$id} = $name;
}

$sth->finish();

@array_to_return = (\@values_array,\%labels_hash);

return(\@array_to_return);

}

#--------------------------------------------------------------------

sub print_origins {

my $page = $_[0];
my $field_info = $_[1];
my $field_name = $_[2];
local $_;

my $origin_return = compile_origins();
my $origin_array = $$origin_return[0];
my $origin_hash = $$origin_return[1];

print $$page->popup_menu(-name => $field_name,
                         -values => $origin_array,
                         -labels => $origin_hash
                        );

}

#--------------------------------------------------------------------

sub print_edit_origins {

my $page = $_[0];
my $field_info = $_[1];
my $field_name = $_[2];
my $db_value = $_[3];
local $_;

my $origin_return = compile_origins();
my $origin_array = $$origin_return[0];
my $origin_hash = $$origin_return[1];

print $$page->popup_menu(-name => $field_name,
                         -values => $origin_array,
                         -labels => $origin_hash,
                         -default => $db_value
                        );

}

#--------------------------------------------------------------------

sub print_types {

my $page = $_[0];
my $field_info = $_[1];
my $field_name = $_[2];
local $_;

my $types_return = compile_types();
my $types_array = $$types_return[0];
my $types_hash = $$types_return[1];

print $$page->popup_menu(-name => $field_name,
                         -values => $types_array,
                         -labels => $types_hash
                        );

}

#--------------------------------------------------------------------

sub print_edit_types {

my $page = $_[0];
my $field_info = $_[1];
my $field_name = $_[2];
my $db_value = $_[3];
my $default = "";
local $_;

my $types_return = compile_types();
my $types_array = $$types_return[0];
my $types_hash = $$types_return[1];

print $$page->popup_menu(-name => $field_name,
                         -values => $types_array,
                         -labels => $types_hash,
                         -default => $db_value
                        );

}

#--------------------------------------------------------------------

sub compile_origins {

my ($sth, $id, $name, @values_array, @labels_hash, @array_to_return);
local $_;

push(@values_array,0);
$labels_hash{"0"} = "Not Applicable";

$sth = $dbh->prepare("select id,name from original_source order by name");
$sth->execute();

while(($id,$name) = $sth->fetchrow_array())
{
  push(@values_array,$id);
  $labels_hash{$id} = $name;
}

$sth->finish();

@array_to_return = (\@values_array,\%labels_hash);

return(\@array_to_return);

}

#--------------------------------------------------------------------

sub get_food_type {

my $type = $_[0];
local $_;
my $sql = "select name from food_type where id = ?";
my $sth = $dbh->prepare($sql);
$sth->execute($type);

my @results = $sth->fetchrow_array();

return($results[0]);

}

#--------------------------------------------------------------------

sub redirect_to_view {

my $page = $_[0];
my $id = $_[1];
my $search_string = $_[2];
my $query = "recipe_id=$id";
local $_;

if($search_string)
{
  $query .= "&search_defined=1&search_string=$search_string";
}

print $$page->redirect("http://$view_cgi"."?"."$query");

}

#--------------------------------------------------------------------

sub redirect_to_results {

my $page = $_[0];
my $search_string = $_[1];
local $_;

print $$page->redirect("http://$search_results_cgi?$$search_string");

}

#--------------------------------------------------------------------

sub redirect_to_delete {

my $page = $_[0];
my $id = $_[1];
my $search_string = $_[2];
my $query = "recipe_id=$id";
local $_;

if($search_string)
{
  $query .= "&search_defined=1&search_string=$search_string";
}

print $$page->redirect("http://$delete_cgi"."?"."$query");

}

#--------------------------------------------------------------------

sub redirect_to_edit {

my $page = $_[0];
my $id = $_[1];
my $search_string = $_[2];
my $query = "recipe_id=$id";
local $_;

if($search_string)
{
  $query .= "&search_defined=1&search_string=$search_string";
}

print $$page->redirect("http://$edit_cgi"."?"."$query");

}

#--------------------------------------------------------------------

sub redirect_to_search {

my $page = $_[0];
my $id = $_[1];
local $_;

print $$page->redirect("http://$search_cgi");

}

#--------------------------------------------------------------------

sub get_original_source {

my $source = $_[0];
local $_;

my $sql = "select name from original_source where id = ?";
my $sth = $dbh->prepare($sql);
$sth->execute($source);

my @results = $sth->fetchrow_array();

return($results[0]);

}

#--------------------------------------------------------------------

sub no_parameter_found {

my $page = $_[0];
local $_;

print_page_header($page);
print $$page->h2({-align=> "center"},"Error");
print $$page->p({-class => "no-id-found"},
                "No recipe was specified to view, edit, or delete.  Please try again.");
print $$page->start_form();
print $$page->p({-align => "center"},$$page->button(-name    => "MainMenuButton",
                     -value   => "Main Menu",
                     -onClick => "MainMenu()"));
print $$page->end_html();

}
	
#--------------------------------------------------------------------

sub include_back_to_search {

my $page = $_[0];
my $search_string;
local $_;

if(defined($$page->url_param('search_string')))
{
  $search_string = $$page->url_param('search_string');
}
else
{
  $search_string = $$page->param('search_string');
}

$search_string =~ s/cgi_equals/=/go;
$search_string =~ s/cgi_amp/\&/go;


print $$page->button(-name	=> "BackToSearch",
                     -value	=> "Back to Search Results",
                     -onClick   => "window.location = \"http://$search_results_cgi?search_defined=1&$search_string\""
                    );
print $$page->hidden(-name	=> 'search_defined',
                     -default	=> 1);
print $$page->hidden(-name	=> 'search_string',
                     -default	=> $search_string);
                     
return 1;

}

#--------------------------------------------------------------------

sub ceil {

my $in = $_[0];
my $whole = int($in);

if($in == $whole) 
{
  return $whole;
} 
else 
{
  return ($whole + 1);
}

}


#--------------------------------------------------------------------

sub print_start_form {

my $page = $_[0];
my $cgi_name = $_[1];
local $_;

print $$page->start_form(-method        => 'post',
                         -action        => $cgi_name);
return 1;

}

#--------------------------------------------------------------------

sub print_session_expired_page {

my $page = $_[0];
local $_;

print $$page->redirect(-uri => "http://$expired_cgi");

return 1;

}

#--------------------------------------------------------------------

sub brsrch_determine_record_locked {

my $page = $_[0];
my $locked = $_[1];
my $locked_until = $_[2];
my $locked_session_id = $_[3];
my $user_id = $$page->cookie($id_cookie);
my $session_id = $$page->cookie($session_cookie);
local $_;

if(($locked) && (!(lock_is_expired($locked_until)))
   && ($session_id ne $locked_session_id))
{
  return 1;
}
else
{
  return 0;
}

}

#--------------------------------------------------------------------

sub include_lock_explanation {

my $page = $_[0];
local $_;

use lib ".";
use PhraseManager;
setup_phrases();

print $$page->start_table({-border => 0,
                           -cellpadding => 3,
                           -cellspacing => 3});
print $$page->Tr($$page->td({-align => 'center'},
                            $$page->img({-src => $small_lock_image,
                                         -alt => $$phrases[19]})
                           ),
                 $$page->td({-class => 'lock-explanation-text'},
                            $$phrases[19]
                           )
                );

print $$page->Tr($$page->td({-align => 'center'},
                            $$page->img({-src => $small_break_lock_image,
                                         -alt => $$phrases[18]})
                           ),
                 $$page->td({-class => 'lock-explanation-text'},
                            $$phrases[18]
                           )
                );

print $$page->end_table();

return 1;

}

#--------------------------------------------------------------------

sub redirect_if_locked {

my $page = $_[0];
my $record_id = $_[1];
my $session_id = $$page->cookie($session_cookie);
my ($sth,$ok,$locked,$locked_until,$sql,$locked_session_id);
local $_;

$sql = 'select locked,locked_until,locked_session_id from recipes where id = ?'
;
$sth = $dbh->prepare($sql);
$sth->execute($record_id);

($locked,$locked_until,$locked_session_id) = $sth->fetchrow_array();

$sth->finish();

if(($locked) && (!(lock_is_expired($locked_until))) &&
   ($locked_session_id ne $session_id))
{
  redirect_to_read_only($page,$record_id);
  return 1;
}
else
{
  return 0;
}

}

#--------------------------------------------------------------------

sub establish_lock {

my ($page,$id,) = @_;
my $lock_end_time = time() + $lock_timeout;
my ($sth,$sql,$ok,$user_id,$session_id);
local $_;

if(defined($$page->cookie($id_cookie)))
{
  $user_id = $$page->cookie($id_cookie);
}
else
{
  $user_id = -1;
}

if(defined($$page->cookie($session_cookie)))
{
  $session_id = $$page->cookie($session_cookie);
}
else
{
  $session_id = -1;
}



$sql = 'update recipes set locked = 1,locked_by = ?,locked_until = ?,'.
       'locked_session_id = ? where id = ?';
$sth = $dbh->prepare($sql);
$ok = $sth->execute($user_id,$lock_end_time,$session_id,$id);

if(!($ok))
{
  die("Could not establish lock on id $id for user_id $user_id until $lock_end_t
ime:  $!\n");
}

return 1;

}

#--------------------------------------------------------------------

sub release_lock {

my $id = $_[0];
my ($sth,$sql,$ok);
local $_;

$sql = 'update recipes set locked = 0 where id = ?';
$sth = $dbh->prepare($sql);
$ok = $sth->execute($id);

if(!($ok))
{
  die("Could not remove lock on id $id:  $!\n");
}

return 1;

}

#--------------------------------------------------------------------

sub lock_is_expired {

my $lock_time_end = $_[0] ? $_[0] : 1;
my $current_lock_time = time();
local $_;

if($lock_time_end <= $current_lock_time)
{
  return 1;
}
else
{
  return 0;
}

}

#--------------------------------------------------------------------

sub reverse_user_id {

my $user_id = $_[0];
my ($sth,$results);
local $_;

if($user_id)
{
  $sth = $dbh->prepare("select name from recipe_users where id = $user_id");
  $sth->execute();
  ($results) = $sth->fetchrow_array;
  unless($results)
  {
    die("I was not able to reverse $user_id to a name using the users table:  $!
\n");
  }
}
else
{
  die("reverse_user_id was called without a valid $user_id!\n");
}

return($results);

}

#--------------------------------------------------------------------

sub this_user_allowed_to_break_lock {

my $page = $_[0];
my $locked_by_id = $_[1];
my $current_user_id = $$page->cookie($id_cookie);
local $_;

if($current_user_id == $locked_by_id)
{
  return 1;
}
else
{
  return 0;
}

}

#--------------------------------------------------------------------

sub redirect_to_read_only {

my $page = $_[0];
my $id = $_[1];
my $search_string = $$page->param('search_string');
my $query = "recipe_id=$id";
local $_;

if($search_string)
{
  $query .= "&search_defined=1&search_string=$search_string";
}

$query .= embed_results_page_display_nav($page);

print $$page->redirect("http://${read_only_cgi}?${query}");

return 1;

}

#--------------------------------------------------------------------

sub embed_results_page_display_nav {

my $page = $_[0];
local $_;

if(defined($$page->param('display_all_records')))
{
  return "&display_all_records=1";
}
elsif(defined($$page->param('page')))
{
  my $page_number = $$page->param('page');
  return("&page=$page_number");
}
else
{
  return("");
}

}

#--------------------------------------------------------------------

sub remove_trailing_whitespace {

my $string = $_[0];
local $_;

$string =~ s/\s*$//;

return ($string);

}

#--------------------------------------------------------------------

sub transform_search_string {

my $string = $_[0];
local $_;

$$string =~ s/\&$//o;
$$string =~ s/=/cgi_equals/go;
$$string =~ s/\&/cgi_amp/go;

return 1;

}

#--------------------------------------------------------------------

sub reverse_search_string_transform {

my $string = $_[0];
local $_;

$$string =~ s/cgi_equals/=/go;
$$string =~ s/cgi_amp/\&/go;

return 1;

}

#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------

1;
