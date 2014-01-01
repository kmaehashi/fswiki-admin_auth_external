package plugin::admin_auth_external::AccountHandler;

# admin_auth_external
# @author Kenichi Maehashi

use strict;

sub new {
	my $class = shift;
	my $self = {};
	return bless $self, $class;
}

sub do_action {
	my $self = shift;
	my $wiki = shift;

	# non-local users cannot change their information
	my $id = $wiki->get_login_info()->{id};
	return $wiki->error(
		"ユーザ " . $id . " はローカルユーザではないため、情報を変更することはできません。");
};

1;
