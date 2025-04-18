{pkgs}: {
  deps = [
    pkgs.pkg-config
    pkgs.libffi
    pkgs.libsodium
    pkgs.libxcrypt
    pkgs.glibcLocales
    pkgs.cacert
    pkgs.psmisc
    pkgs.postgresql
    pkgs.openssl
  ];
}
