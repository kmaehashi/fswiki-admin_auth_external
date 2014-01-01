############################################################
#
# ユーザ認証を外部のモジュールに委譲します。
#
############################################################

# admin_auth_external
# @author Kenichi Maehashi

package plugin::admin_auth_external::Install;

use strict;

# overwrite Util::cookie_path to generate Wiki-wide cookie (for Wiki Farms)
&wikiwide_cookie_path();

sub install {
	my $wiki = shift;
	my $cgi = $wiki->get_CGI;

	my $session = $cgi->get_session($wiki);

	# if the current user is an external user
	if (defined $session && defined $session->param("wiki_id_external")) {
		my $info = $wiki->get_login_info();
		my $ext_id = $session->param("wiki_id_external");
		if (defined $info && $info->{id} ne '') {
			if ($info->{id} ne $ext_id) {
				# he was a non-local user but re-authenticated as a local user; do nothing
			} else {
				# he is a non-local user (but he may have a local account)
				if (! $wiki->user_exists($info->{id})) {
					# he is a "pure" non-local user, temporary register him as a user
					$wiki->add_user($info->{id}, '', $info->{type});
				}

				# non-local users cannot change their information (like password)
				$wiki->add_user_handler("ACCOUNT","plugin::admin_auth_external::AccountHandler");

				# non-local users can switch to local user
				$wiki->add_user_menu("ユーザの切り替え", $wiki->create_url({action=>"LOCALLOGIN"}), 0,
							"ローカルユーザとして再認証を行います。");
				$wiki->add_user_handler("LOCALLOGIN","plugin::admin_auth_external::LocalLogin");
			}
		}
	}

	$wiki->add_handler("LOGIN","plugin::admin_auth_external::Login");
}

sub wikiwide_cookie_path() {
	#*Util::cookie_path = sub {
	#	my $wiki = shift;
	#	my $path = $ENV{'SCRIPT_NAME'};
	#	$path =~ s/\/([^\/]+?)$/\//; # dirname($SCRIPT_NAME)
	#	return $path;
	#};
}

1;
