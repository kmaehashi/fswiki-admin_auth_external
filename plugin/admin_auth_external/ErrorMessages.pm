package plugin::admin_auth_external::ErrorMessages;

use strict;

use constant {
	ACCESS_GRANTED => 0,
	ERR_INVALID_ID_PW => 1,
	ERR_INVALID_ID_PW_CANCEL => 2,
	ERR_CANCEL => 3,
	ERR_NO_PRIV => 4,
	ERR_CHANGE_PW => 5,
	ERR_SET_PW => 6,
	ERR_ACCT_INACTIVE => 7,
	ERR_ACCT_SUSPENDED => 8,
	ERR_ACCT_EXPIRED => 9,
	ERR_AUTH_SERV_FAILED => 10,
	ERR_MAINTENANCE => 11,
	ERR_UNEXPECTED => 99,
};

sub get($) {
	my $err = shift;
	my $msg;

	if    ($err ==  ERR_INVALID_ID_PW)        { $msg = "ユーザ名またはパスワードが違います。"; }
	elsif ($err ==  ERR_INVALID_ID_PW_CANCEL) { $msg = "ユーザ名またはパスワードが違うか、認証がキャンセルされました。"; }
	elsif ($err ==  ERR_CANCEL)               { $msg = "認証がキャンセルされました。"; }
	elsif ($err ==  ERR_NO_PRIV)              { $msg = "この操作を行う権限がありません。"; }
	elsif ($err ==  ERR_CHANGE_PW)            { $msg = "このアカウントはパスワードを変更するまで使用できません。"; }
	elsif ($err ==  ERR_SET_PW)               { $msg = "パスワードの設定されていないアカウントではログインできません。"; }
	elsif ($err ==  ERR_ACCT_INACTIVE)        { $msg = "このアカウントはまだ有効化されていません。"; }
	elsif ($err ==  ERR_ACCT_SUSPENDED)       { $msg = "このアカウントは利用停止になっています。"; }
	elsif ($err ==  ERR_ACCT_EXPIRED)         { $msg = "このアカウントの有効期限が切れています。"; }
	elsif ($err ==  ERR_AUTH_SERV_FAILED)     { $msg = "認証サーバに接続できませんでした。"; }
	elsif ($err ==  ERR_MAINTENANCE)          { $msg = "現在システムのメンテナンスを行っているため、ログインできません。"; }
	elsif ($err ==  ERR_UNEXPECTED)           { $msg = "認証中に予期しないエラーが発生しました。管理者までお問い合わせください。"; }
	else                                      { $msg = "エラー(" . int($err) . ")が発生しました。管理者までお問い合わせください。"; }
	return $msg;
}

1;
