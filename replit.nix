{ pkgs }: {
  deps = [
    # Python and backend dependencies
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.postgresql_15

    # Node.js and frontend dependencies
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.nodePackages.typescript
    pkgs.nodePackages.typescript-language-server

    # Language servers
    pkgs.python311Packages.python-lsp-server

    # Build tools
    pkgs.gcc
    pkgs.gnumake
    pkgs.pkg-config

    # Image processing (for reportlab/pillow)
    pkgs.libjpeg
    pkgs.zlib
    pkgs.freetype
    pkgs.lcms2
    pkgs.openjpeg
    pkgs.libtiff
    pkgs.libwebp

    # PostgreSQL client libraries
    pkgs.postgresql_15.lib

    # Other utilities
    pkgs.curl
    pkgs.git
  ];

  # Environment variables
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.postgresql_15.lib
    ];
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.postgresql_15.lib
    ];
    PYTHONBIN = "${pkgs.python311}/bin/python3.11";
    LANG = "en_US.UTF-8";
    PGDATA = "$REPL_HOME/pgdata";
  };
}
