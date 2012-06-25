package 	PhraseManager;
#require		Exporter;
use		AutoLoader 'AUTOLOAD';
#
# AutoSplit with
# perl -e 'use AutoSplit; autosplit($ARGV[0], $ARGV[1], 0, 1, 1)' PhraseManager.pm auto
#
our @ISA	= qw(Exporter);
our @EXPORT	= qw($phrases setup_phrases);
our @EXPORT_OK	= qw();
our $VERSION	= 0.9;

use strict;

our ($phrases);

$XML::Simple::PREFERRED_PARSER='XML::SAX::Expat';

#####################################################################

1;
__END__

#--------------------------------------------------------------------

sub setup_phrases {

my $config_file = "/home/dbogen/userland/projects/recipes/phrase-config.xml";
my $config;
my $xml_obj = new XML::Simple;
local $_;

$config = $xml_obj->XMLin($config_file,
                          NormalizeSpace => 2,
                          ForceArray => ['phrase']);

$phrases = $config->{'phrases'}->{'phrase'};

return 1;

}

1;
