#!/bin/bash
# Installs terminal-mac @VERSION@ (build @BUILD@):
#   curl -fsSL https://github.com/@REPO@/releases/latest/download/get.sh | bash
# Options pass through to install.sh, for example: | bash -s -- --prefix "$HOME/.local"
# Downloads one signed archive from GitHub, verifies its SHA-256, then installs it under
# ~/.local without administrator rights. VM data is never touched.
set -euo pipefail
archive='@ARCHIVE@'
url='https://github.com/@REPO@/releases/download/@TAG@/@ARCHIVE@'
sha256='@SHA256@'
[[ "$(uname -s)" = Darwin && "$(uname -m)" = arm64 ]] || { echo 'terminal-mac requires a Mac with Apple silicon.' >&2; exit 1; }
os_major="$(sw_vers -productVersion)"; os_major="${os_major%%.*}"
[[ "$os_major" -ge 14 ]] || { echo 'terminal-mac requires macOS 14 or later.' >&2; exit 1; }
work="$(mktemp -d "${TMPDIR:-/tmp}/terminal-mac-get.XXXXXX")"
trap 'rm -rf "$work"' EXIT
echo "Downloading terminal-mac @VERSION@…"
curl -fL --progress-bar "$url" -o "$work/$archive"
echo "$sha256  $work/$archive" | shasum -a 256 -c - >/dev/null || { echo 'Checksum mismatch; nothing was installed.' >&2; exit 1; }
ditto -x -k "$work/$archive" "$work/unpacked"
bash "$work/unpacked/${archive%.zip}/install.sh" "$@"
cat <<'TEXT'

Next:
  terminal-mac                                      # create and open your virtual Mac
  axim mcp add terminal-mac -- terminal-mac mcp     # computer-use tools for AXIM
  terminal-mac skills install                       # the agent skill (~/.axim/skills)
  terminal-mac mcp --config                         # config for AXIM, Cursor, VS Code…
TEXT
