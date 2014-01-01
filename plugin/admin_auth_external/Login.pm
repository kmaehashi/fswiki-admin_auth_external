package plugin::admin_auth_external::Login;

# admin_auth_external
# @author Kenichi Maehashi

use strict;
use base qw(plugin::admin::Login);

use plugin::admin_auth_external::ErrorMessages;

our $LOGIN_MODULE_NAME = "login.cgi";

sub new {
	my $class = shift;
	my $self = new plugin::admin::Login;
	return bless $self;
}

sub do_action {
	my $self = shift;
	my $wiki = shift;
	my $cgi = $wiki->get_CGI;

	if (defined $wiki->get_login_info()) {
		# user successfully logged in
		# if this is a new login request (i.e., user switching), throw login_info away to handle local authentication
		if ($cgi->param('id') ne '') {
			$wiki->{'login_info'} = undef;
		}
		return $self->SUPER::do_action($wiki);

	} elsif (defined $cgi->param('stat')) {
		my $err = int($cgi->param('stat'));
		my $msg;
		if ($err == 0) {
			# login modules says its ok but the session record is not set
			$msg = "ログインモジュールがセッションを開始できませんでした。Cookie を有効に設定して、もう一度ログインしてください。";
		} else {
			# login module says that there was an error authenticating user
			$msg = plugin::admin_auth_external::ErrorMessages::get($err);
		}
		return $wiki->error($msg);

	} else {
		# the user clicked an "Login" link of the header; authenticate as a non-local user using login module
		my $url = $cgi->url();
		$url =~ s/\/([^\/]*?)$/\/$LOGIN_MODULE_NAME/; # dirname(URL) . "/" . $LOGIN_MODULE_NAME
		$url .= $cgi->path_info(); # append Wiki Farm path
		# TODO defined $cgi->param('logout') && logout mode
		$url =~ s/[\r\n]//g;

		print "Location: " . $url . "\n";
		print "\n";
		exit;
	}
}

1;
