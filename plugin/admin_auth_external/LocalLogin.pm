package plugin::admin_auth_external::LocalLogin;

# admin_auth_external
# @author Kenichi Maehashi

use strict;

use base qw(plugin::admin::Login);

sub new {
	my $class = shift;
	my $self = new plugin::admin::Login;
	return bless $self;
}

sub do_action {
	my $self = shift;
	my $wiki = shift;
	my $cgi = $wiki->get_CGI;
	my $data;

	# we should throw login_info away so that plugin::admin::Login shows the login form
	$wiki->{'login_info'} = undef;

	# get login form
	$data = $self->SUPER::do_action($wiki);

	# overwrite title
	$wiki->set_title("ユーザの切り替え");

	return $data;
}

1;
