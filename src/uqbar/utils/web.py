# SPDX-License-Identifier: MIT
# uqbar/utils/web.py
"""
Uqbar | Utils | Web
===================

Overview
--------
Placeholder.

Metadata
--------
- Project: Uqbar
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Final
from urllib.parse import unquote, urlparse

from uqbar.utils.executor import execute

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
# Conservative filename sanitizer (keeps unicode letters/digits; removes path
# separators/control chars)
_INVALID_CHARS_RE: Final[re.Pattern[str]] = re.compile(r'[\\/\x00-\x1f\x7f]+')

_WHITESPACE_RE: Final[re.Pattern[str]] = re.compile(r"\s+")


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _safe_filename(name: str) -> str:
    name = name.strip()
    name = _INVALID_CHARS_RE.sub("_", name)
    name = _WHITESPACE_RE.sub(" ", name)
    # Avoid Windows reserved names and trailing dots/spaces
    name = name.strip(" .")
    if not name:
        return ""
    # Very defensive: limit length
    return name[:240]


def _unique_path(dest: Path) -> Path:
    """If dest exists, append ' (n)' before the suffix."""
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    for i in range(1, 10_000):
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find a unique filename for: {dest}")


def _guess_name_from_url(download_url: str) -> str:
    p = urlparse(download_url)
    # Prefer last path segment
    last = (p.path.split("/")[-1] if p.path else "").strip()
    last = unquote(last)  # decode %XX
    return _safe_filename(last)


def _guess_ext_from_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    ct = content_type.split(";", 1)[0].strip().lower()
    mapping = {
        "text/plain": ".txt",
        "text/html": ".html",
        "application/pdf": ".pdf",
        "application/json": ".json",
        "text/csv": ".csv",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
        "application/zip": ".zip",
        "application/gzip": ".gz",
        "application/x-tar": ".tar",
    }
    return mapping.get(ct)


# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def download_path_wget(
    download_url: str,
    output_path: Path,
) -> tuple[str | None, str | None]:
    """
    Downloads the argument path.

    GNU Wget 1.25.0, a non-interactive network retriever.
    Usage: wget [OPTION]... [URL]...

    Mandatory arguments to long options are mandatory for short options too.

    Startup:
      -V,  --version                   display the version of Wget and exit
      -h,  --help                      print this help
      -b,  --background                go to background after startup
      -e,  --execute=COMMAND           execute a `.wgetrc'-style command

    Logging and input file:
      -o,  --output-file=FILE          log messages to FILE
      -a,  --append-output=FILE        append messages to FILE
      -d,  --debug                     print lots of debugging information
      -q,  --quiet                     quiet (no output)
      -v,  --verbose                   be verbose (this is the default)
      -nv, --no-verbose                turn off verboseness, without being quiet
           --report-speed=TYPE         output bandwidth as TYPE.  TYPE can be bits
      -i,  --input-file=FILE           download URLs found in local or external FILE
      -F,  --force-html                treat input file as HTML
      -B,  --base=URL                  resolves HTML input-file links (-i -F)
                                         relative to URL
           --config=FILE               specify config file to use
           --no-config                 do not read any config file
           --rejected-log=FILE         log reasons for URL rejection to FILE

    Download:
      -t,  --tries=NUMBER              set number of retries to NUMBER (0 unlimits)
           --retry-connrefused         retry even if connection is refused
           --retry-on-host-error       consider host errors as non-fatal, transient errors
           --retry-on-http-error=ERRORS    comma-separated list of HTTP errors to retry
      -O,  --output-document=FILE      write documents to FILE
      -nc, --no-clobber                skip downloads that would download to
                                         existing files (overwriting them)
           --no-netrc                  don't try to obtain credentials from .netrc
      -c,  --continue                  resume getting a partially-downloaded file
           --start-pos=OFFSET          start downloading from zero-based position OFFSET
           --progress=TYPE             select progress gauge type
           --show-progress             display the progress bar in any verbosity mode
      -N,  --timestamping              don't re-retrieve files unless newer than
                                         local
           --no-if-modified-since      don't use conditional if-modified-since get
                                         requests in timestamping mode
           --no-use-server-timestamps  don't set the local file's timestamp by
                                         the one on the server
      -S,  --server-response           print server response
           --spider                    don't download anything
      -T,  --timeout=SECONDS           set all timeout values to SECONDS
           --dns-timeout=SECS          set the DNS lookup timeout to SECS
           --connect-timeout=SECS      set the connect timeout to SECS
           --read-timeout=SECS         set the read timeout to SECS
      -w,  --wait=SECONDS              wait SECONDS between retrievals
                                         (applies if more then 1 URL is to be retrieved)
           --waitretry=SECONDS         wait 1..SECONDS between retries of a retrieval
                                         (applies if more then 1 URL is to be retrieved)
           --random-wait               wait from 0.5*WAIT...1.5*WAIT secs between retrievals
                                         (applies if more then 1 URL is to be retrieved)
           --no-proxy                  explicitly turn off proxy
      -Q,  --quota=NUMBER              set retrieval quota to NUMBER
           --bind-address=ADDRESS      bind to ADDRESS (hostname or IP) on local host
           --limit-rate=RATE           limit download rate to RATE
           --no-dns-cache              disable caching DNS lookups
           --restrict-file-names=OS    restrict chars in file names to ones OS allows
           --ignore-case               ignore case when matching files/directories
      -4,  --inet4-only                connect only to IPv4 addresses
      -6,  --inet6-only                connect only to IPv6 addresses
           --prefer-family=FAMILY      connect first to addresses of specified family,
                                         one of IPv6, IPv4, or none
           --user=USER                 set both ftp and http user to USER
           --password=PASS             set both ftp and http password to PASS
           --ask-password              prompt for passwords
           --use-askpass=COMMAND       specify credential handler for requesting
                                         username and password.  If no COMMAND is
                                         specified the WGET_ASKPASS or the SSH_ASKPASS
                                         environment variable is used.
           --no-iri                    turn off IRI support
           --local-encoding=ENC        use ENC as the local encoding for IRIs
           --remote-encoding=ENC       use ENC as the default remote encoding
           --unlink                    remove file before clobber
           --xattr                     turn on storage of metadata in extended file attributes

    Directories:
      -nd, --no-directories            don't create directories
      -x,  --force-directories         force creation of directories
      -nH, --no-host-directories       don't create host directories
           --protocol-directories      use protocol name in directories
      -P,  --directory-prefix=PREFIX   save files to PREFIX/..
           --cut-dirs=NUMBER           ignore NUMBER remote directory components

    HTTP options:
           --http-user=USER            set http user to USER
           --http-password=PASS        set http password to PASS
           --no-cache                  disallow server-cached data
           --default-page=NAME         change the default page name (normally
                                         this is 'index.html'.)
      -E,  --adjust-extension          save HTML/CSS documents with proper extensions
           --ignore-length             ignore 'Content-Length' header field
           --header=STRING             insert STRING among the headers
           --compression=TYPE          choose compression, one of auto, gzip and none. (default: none)
           --max-redirect              maximum redirections allowed per page
           --proxy-user=USER           set USER as proxy username
           --proxy-password=PASS       set PASS as proxy password
           --referer=URL               include 'Referer: URL' header in HTTP request
           --save-headers              save the HTTP headers to file
      -U,  --user-agent=AGENT          identify as AGENT instead of Wget/VERSION
           --no-http-keep-alive        disable HTTP keep-alive (persistent connections)
           --no-cookies                don't use cookies
           --load-cookies=FILE         load cookies from FILE before session
           --save-cookies=FILE         save cookies to FILE after session
           --keep-session-cookies      load and save session (non-permanent) cookies
           --post-data=STRING          use the POST method; send STRING as the data
           --post-file=FILE            use the POST method; send contents of FILE
           --method=HTTPMethod         use method "HTTPMethod" in the request
           --body-data=STRING          send STRING as data. --method MUST be set
           --body-file=FILE            send contents of FILE. --method MUST be set
           --content-disposition       honor the Content-Disposition header when
                                         choosing local file names (EXPERIMENTAL)
           --content-on-error          output the received content on server errors
           --auth-no-challenge         send Basic HTTP authentication information
                                         without first waiting for the server's
                                         challenge

    HTTPS (SSL/TLS) options:
           --secure-protocol=PR        choose secure protocol, one of auto, SSLv2,
                                         SSLv3, TLSv1, TLSv1_1, TLSv1_2, TLSv1_3 and PFS
           --https-only                only follow secure HTTPS links
           --no-check-certificate      don't validate the server's certificate
           --certificate=FILE          client certificate file
           --certificate-type=TYPE     client certificate type, PEM or DER
           --private-key=FILE          private key file
           --private-key-type=TYPE     private key type, PEM or DER
           --ca-certificate=FILE       file with the bundle of CAs
           --ca-directory=DIR          directory where hash list of CAs is stored
           --crl-file=FILE             file with bundle of CRLs
           --pinnedpubkey=FILE/HASHES  Public key (PEM/DER) file, or any number
                                       of base64 encoded sha256 hashes preceded by
                                       'sha256//' and separated by ';', to verify
                                       peer against
           --random-file=FILE          file with random data for seeding the SSL PRNG

           --ciphers=STR           Set the priority string (GnuTLS) or cipher list string (OpenSSL) directly.
                                       Use with care. This option overrides --secure-protocol.
                                       The format and syntax of this string depend on the specific SSL/TLS engine.
    HSTS options:
           --no-hsts                   disable HSTS
           --hsts-file                 path of HSTS database (will override default)

    FTP options:
           --ftp-user=USER             set ftp user to USER
           --ftp-password=PASS         set ftp password to PASS
           --no-remove-listing         don't remove '.listing' files
           --no-glob                   turn off FTP file name globbing
           --no-passive-ftp            disable the "passive" transfer mode
           --preserve-permissions      preserve remote file permissions
           --retr-symlinks             when recursing, get linked-to files (not dir)

    FTPS options:
           --ftps-implicit                 use implicit FTPS (default port is 990)
           --ftps-resume-ssl               resume the SSL/TLS session started in the control connection when
                                             opening a data connection
           --ftps-clear-data-connection    cipher the control channel only; all the data will be in plaintext
           --ftps-fallback-to-ftp          fall back to FTP if FTPS is not supported in the target server
    WARC options:
           --warc-file=FILENAME        save request/response data to a .warc.gz file
           --warc-header=STRING        insert STRING into the warcinfo record
           --warc-max-size=NUMBER      set maximum size of WARC files to NUMBER
           --warc-cdx                  write CDX index files
           --warc-dedup=FILENAME       do not store records listed in this CDX file
           --no-warc-compression       do not compress WARC files with GZIP
           --no-warc-digests           do not calculate SHA1 digests
           --no-warc-keep-log          do not store the log file in a WARC record
           --warc-tempdir=DIRECTORY    location for temporary files created by the
                                         WARC writer

    Recursive download:
      -r,  --recursive                 specify recursive download
      -l,  --level=NUMBER              maximum recursion depth (inf or 0 for infinite)
           --delete-after              delete files locally after downloading them
      -k,  --convert-links             make links in downloaded HTML or CSS point to
                                         local files
           --convert-file-only         convert the file part of the URLs only (usually known as the basename)
           --backups=N                 before writing file X, rotate up to N backup files
      -K,  --backup-converted          before converting file X, back up as X.orig
      -m,  --mirror                    shortcut for -N -r -l inf --no-remove-listing
      -p,  --page-requisites           get all images, etc. needed to display HTML page
           --strict-comments           turn on strict (SGML) handling of HTML comments

    Recursive accept/reject:
      -A,  --accept=LIST               comma-separated list of accepted extensions
      -R,  --reject=LIST               comma-separated list of rejected extensions
           --accept-regex=REGEX        regex matching accepted URLs
           --reject-regex=REGEX        regex matching rejected URLs
           --regex-type=TYPE           regex type (posix)
      -D,  --domains=LIST              comma-separated list of accepted domains
           --exclude-domains=LIST      comma-separated list of rejected domains
           --follow-ftp                follow FTP links from HTML documents
           --follow-tags=LIST          comma-separated list of followed HTML tags
           --ignore-tags=LIST          comma-separated list of ignored HTML tags
      -H,  --span-hosts                go to foreign hosts when recursive
      -L,  --relative                  follow relative links only
      -I,  --include-directories=LIST  list of allowed directories
           --trust-server-names        use the name specified by the redirection
                                         URL's last component
      -X,  --exclude-directories=LIST  list of excluded directories
      -np, --no-parent                 don't ascend to the parent directory

    Email bug reports, questions, discussions to <bug-wget@gnu.org>
    and/or open issues at

    Notes
    -----
    - Does not rely on shell aliases.
    - Avoids shell redirection; writes output via Python.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command: list[str] = (
        [  # --no-clobber --page-requisites --convert-links --adjust-extension
            "wget",
            "-c",
            "--tries=10",
            "-T",
            "10" "--span-hosts",
            (
                "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit"
                "/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36'"
            ),
            "-P",
            str(output_path),
            str(download_url),
        ]
    )

    stdout, stderr = execute(
        full_command=command,
        capture_output=True,
        text=True,
        check=True,
    )

    download_path: Path = output_path / str(download_url.split("/")[-1].strip())
    download_path.resolve()

    return stdout, stderr


def download_url_to_path(
    download_url: str,
    output_path: Path,
) -> tuple[str | None, str | None]:
    """
    Download a URL to a directory, preserving the filename when possible.

    Returns:
        (saved_file_path, info_message_or_warning)
        - saved_file_path: absolute path of the downloaded file, or None on failure
        - info_message_or_warning: None on clean success, else a human-readable note
          (e.g. "filename was inferred", "server provided filename", "error: ...")

    Notes:
      - Uses urllib from the stdlib (no extra deps).
      - Tries to preserve the URL's filename; falls back to server-provided name; then to 'downloaded_file'.
      - Avoids overwriting by auto-suffixing " (n)" if a file already exists.
    """
    try:
        output_dir = Path(output_path).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        if not output_dir.is_dir():
            return None, f"error output_path is not a directory: {output_dir}"

        # First guess: from URL path (decoded)
        guessed_name = _guess_name_from_url(download_url)

        req = urllib.request.Request(
            download_url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; download_url_to_path/1.0)",
                "Accept": "*/*",
            },
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            # Try to use server-suggested filename if URL doesn't have one
            server_filename = None
            try:
                # get_filename reads Content-Disposition, when present
                server_filename = resp.info().get_filename()
            except Exception:
                server_filename = None

            content_type = resp.info().get("Content-Type")
            note_parts: list[str] = []

            final_name = guessed_name
            if not final_name and server_filename:
                final_name = _safe_filename(server_filename)
                if final_name:
                    note_parts.append("filename taken from content disposition")

            if not final_name:
                final_name = "downloaded_file"
                note_parts.append("filename could not be determined; using downloaded_file")

            # If no extension, maybe infer from content-type
            if "." not in Path(final_name).name:
                ext = _guess_ext_from_content_type(content_type)
                if ext:
                    final_name = f"{final_name}{ext}"
                    note_parts.append("extension inferred from content type")

            dest = _unique_path(output_dir / final_name)

            # Stream to disk
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 64)
                    if not chunk:
                        break
                    f.write(chunk)

        # Basic post-check
        if dest.stat().st_size == 0:
            # Don't auto-delete; just report
            note_parts.append("warning downloaded file is empty")

        return str(dest), ("; ".join(note_parts) if note_parts else None)

    except Exception as e:
        return None, f"error {type(e).__name__} {e}"


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "download_path_wget",
    "download_url_to_path",
]
