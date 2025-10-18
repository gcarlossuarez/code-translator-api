{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.chromium
    pkgs.chromedriver
    # Dependencias necesarias para ChromeDriver
    pkgs.xorg.libX11
    pkgs.xorg.libXcomposite
    pkgs.xorg.libXdamage
    pkgs.xorg.libXext
    pkgs.xorg.libXfixes
    pkgs.xorg.libXrandr
    pkgs.nss
    pkgs.nspr
    pkgs.atk
    pkgs.cups
    pkgs.gtk3
    pkgs.pango
    pkgs.cairo
    pkgs.gdk-pixbuf
    pkgs.glib
    pkgs.dbus
    pkgs.at-spi2-atk
    pkgs.at-spi2-core
    pkgs.libdrm
    pkgs.mesa
    pkgs.expat
    pkgs.alsa-lib
  ];
}