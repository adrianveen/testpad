This folder can contain pre-baked Matplotlib font cache files
to speed up the first use of plotting in the packaged app.

Drop files named like:
  fontlist-<mpl-version>-<hash>.json

If present, the runtime hook will copy them to a writable
per-user MPLCONFIGDIR so Matplotlib can read them without
rebuilding. If none are present, Matplotlib will build the
cache on first use.

