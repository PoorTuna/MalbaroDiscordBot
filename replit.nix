{pkgs}: {
  deps = [
    pkgs.libxcrypt
    pkgs.glibcLocales
    pkgs.cacert
    pkgs.psmisc
    pkgs.postgresql
    pkgs.openssl
  ];
}
