#!/usr/bin/perl --

###############################################################################
# admin_auth_external - External Login Module
# @author Kenichi Maehashi
###############################################################################

use lib './lib';

# for development
use strict;
use warnings;
no warnings 'redefine'; # we use redefinition
use CGI::Carp qw/fatalsToBrowser/;

use HTML::Template;
use Wiki;
use Util;
use plugin::admin_auth_external::Install;
use plugin::admin_auth_external::ErrorMessages;

# Prototypes
our ($wiki, $cgi, $script_name, $my_script_name, $path_info, $local_users);
sub login_external($$$);
sub login_local($$);
sub find_local_user($);
sub grant_access($$$$$$);
sub redirect_to_url($);

###############################################################################
# Configuration - CUSTOMIZE HERE!
###############################################################################
# Default privilege for non-local users; 0 for administrator, 1 for standard user.
my $DEFAULT_TYPE = 1;

# Override the user type if the user is in the local user database; 1 to override,
# 0 to not. This is useful when you need to give some of non-local users an admin
# privilege (i.e., create a local admin user with the name of the non-local user).
my $OVERRIDE_TYPE = 1;

# Non-local users MUST exist in the local user table; 1 for Yes, 0 for No.
# If the user is not in the local user table, the authorization will be rejected,
# even if the password is correct. Note that password in the local database will
# NOT be verified!
my $LOCAL_MANDATORY = 0;

# When the external module failed to authenticate the user, try using the local
# user table for authentication; 1 for Yes, 0 for No. If you are using Apache
# module-based authentication (as we need raw password to use local user table),
# or $LOCAL_MANDATORY parameter is set to 1, you cannot enable fallback.
my $FALLBACK_TO_LOCAL = 0;

###############################################################################
# Fetch username and password - CUSTOMIZE HERE!
###############################################################################
sub get_input() {
	my ($id, $pass);

	# ---------------------------------------------------------------

	# Authenticate using Apache module
	$id = $ENV{'REMOTE_USER'};
	$pass = '';

	# or if you have a HTML form input:
	# $id = $cgi->param('user_id');
	# $pass = $cgi->param('user_password');

	# ---------------------------------------------------------------

	return ($id, $pass);
}

###############################################################################
# Verify given id and password using the external source - CUSTOMIZE HERE!
###############################################################################
sub login_external($$$) {
	my ($id, $pass, $path) = @_;
	my ($stat, $type) = (1, $DEFAULT_TYPE);

	# Deny access if the user ID is empty or the password is not defined
	if (not (defined $id && $id ne '') || not (defined $pass)) {
		$stat = 3; # ACCESS DENIED
		return ($stat, $type);
	}

	# ---------------------------------------------------------------

	# You need to write a code to authenticate the user here - connect
	# to an external credential provider and compare the password, for example.
	# set $stat to 0 to allow access, or other values (see error numbers defined
	# in ErrorMessages.pm) to deny access.
	# You can even set the privilege ($type) for the user; 0 for admin.

	# assuming Apache authentication, allow access in any case
	$stat = 0; # ACCESS GRANTED

	# ---------------------------------------------------------------

	return ($stat, $type);
}

###############################################################################
# Verify given id and password using the local database
###############################################################################
sub login_local($$) {
	my ($id, $pass) = @_;
	my ($stat, $type) = (1, $DEFAULT_TYPE);

	my ($local_pass, $local_type) = find_local_user($id);
	if (defined $local_pass && defined $local_type) {
		if (&Util::md5($pass, $id) eq $local_pass) {
			$stat = 0;
			$type = $local_type;
		}
	}

	return ($stat, $type);
}


###############################################################################
# Look for the local user
###############################################################################
sub find_local_user($) {
	my ($id) = @_;

	# lazy-load the local user database
	if (not defined $local_users) {
		$local_users = &Util::load_config_hash($wiki, $wiki->config('userdat_file'));
	}

	# lookup
	foreach my $local_id (keys(%$local_users)) {
		my ($local_pass, $local_type) = split(/\t/, $local_users->{$local_id});
		if ($local_id eq $id) {
			# return password (hashed) and user type
			return ($local_pass, $local_type);
		}
	}

	# not found...
	return (undef, undef);
}

###############################################################################
# Grant access to user by issuing session cookie
###############################################################################
sub grant_access($$$$$$) {
	my ($id, $pass, $type, $override, $path, $is_external) = @_;

	# override pass and type if the user is in the local user database
	if ($override) {
		my ($local_pass, $local_type) = find_local_user($id);
		if (defined $local_pass && defined $local_type) {
			$pass = $local_pass;
			$type = $local_type;
		}
	}

	# patch cookie_path to use wiki.cgi instead of login.cgi
	*Util::cookie_path = sub {
		my $wiki = shift;
		my $cgi = $wiki->get_CGI;
		my $path_info = $cgi->path_info();
		my $cookie_path = $ENV{'REQUEST_URI'};

		$cookie_path =~ s/\/$path_info$//;
		$cookie_path =~ s/\/([^\/]+?)$/\//; # dirname($cookie_path)
		return $cookie_path;
	};

	# generate session cookies; wiki_id_external indicates that the user is not a local one
	my $session = $cgi->get_session($wiki, 1);
	$session->param("wiki_id",          $id);
	$session->param("wiki_id_external", $id) if ($is_external);
	$session->param("wiki_type",        $type);
	$session->param("wiki_path",        $path);
	$session->flush();
}

###############################################################################
# ENTRY POINT
###############################################################################

# overwrite Util::cookie_path to generate Wiki-wide cookie
&plugin::admin_auth_external::Install::wikiwide_cookie_path();

# create new Wiki instance and set global variables
$wiki = Wiki->new('setup.dat');
$cgi = $wiki->get_CGI;
$script_name = $wiki->config('script_name'); # usually "wiki.cgi"
$my_script_name = $0; # usually "login.cgi"
$path_info = $cgi->path_info(); # name of the Wiki Farm
$local_users = undef; # lazy load

# use log_dir as a session directory
$wiki->config('session_dir', $wiki->config('log_dir'));

# is the request for a farm?
if (length($path_info) > 0) {
	# check if the farm exists
	unless ($path_info =~ m<^(/[A-Za-z0-9]+)*/?$> and -d $wiki->config('data_dir') . $path_info) {
		die "Wiki farm not found!";
	}

	# remove trailing slash
	$path_info =~ s/\/$//;

	# rewrite directories
	$wiki->config('config_dir' , $wiki->config('config_dir') . $path_info);
	$wiki->config('log_dir'    , $wiki->config('log_dir'   ) . $path_info);
}

# begin login process
my ($id, $pass, $type, $stat);
my $is_external = 1; # is this an external account?

# get user's ID and password
($id, $pass) = get_input();

# try to authenticate using external authenticator
($stat, $type) = login_external($id, $pass, $path_info);

if ($LOCAL_MANDATORY) {
	# when local_mandatory is set, user must be in the local user database
	if ($stat == 0) {
		my ($local_pass, $local_type) = find_local_user($id);
		if (!(defined $local_pass) || !(defined $local_type)) {
			$stat = 1;
		}
	}
} elsif ($FALLBACK_TO_LOCAL) {
	# when externa auth. failed, try the local database, if FALLBACK_TO_LOCAL is set
	if ($stat != 0) {
		($stat, $type) = login_local($id, $pass);
		$is_external = 0;
	}
}

# is the user authorized?
if ($stat == 0) {
	grant_access($id, $pass, $type, $OVERRIDE_TYPE, $path_info, $is_external);
}

# redirect
$wiki->redirectURL($wiki->create_url({'action' => 'LOGIN', 'stat' => $stat}));
