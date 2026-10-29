# Shared helpers for the SpecDock runner scripts on Linux and macOS (iss-00463). Sourced, not executed.

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d ' ' -f 1
}

# Downloads URL to FILE unless FILE already has the SHA256. A cached file with another digest is fetched again once,
# so a truncated download does not fail every later run.
fetch_verified() {
  if [ -f "$2" ] && [ "$(sha256_of "$2")" = "$3" ]; then return 0; fi
  rm -f -- "$2" "$2.part"
  curl -fsSL -o "$2.part" "$1"
  if [ "$(sha256_of "$2.part")" != "$3" ]; then
    rm -f -- "$2.part"
    echo "SHA256 of $1 is not $3" >&2
    return 1
  fi
  mv -- "$2.part" "$2"
}

# Sets each KEY=VALUE line in the runner's .env FILE: drops earlier lines for the same keys, keeps the rest and prints
# "changed" when the file changed. The runner user runs it on its own file, so root never opens that file.
set_env_lines() {
  file=$1
  shift
  touch -- "$file"
  new=$(mktemp "$file.XXXXXX")
  {
    for line in "$@"; do printf '%s\n' "${line%%=*}"; done
    echo
    cat -- "$file"
  } | awk 'blank { split($0, kv, "="); if (!(kv[1] in keys)) print; next } /^$/ { blank = 1; next } { keys[$0] }' >"$new"
  printf '%s\n' "$@" >>"$new"
  if cmp -s -- "$new" "$file"; then rm -f -- "$new"; else mv -- "$new" "$file" && echo changed; fi
}

# Prints "<uid> <permission bits>" of a path without following a final link, with GNU or BSD stat.
owner_mode() { stat -c '%u %a' "$1" 2>/dev/null || stat -f '%u %Lp' "$1"; }

# Fails unless DIR and its entries are real files owned by root or OWNER_UID that no one else can write, so root runs
# nothing a runner user could have replaced.
require_private_copy() {
  for path in "$1" "$1"/*; do
    if [ -L "$path" ] || ! owner_mode "$path" | grep -q -E "^(0|$2) [0-7]?[0-7][0145][0145]\$"; then
      echo "refusing to run from $path: it must be owned by root or uid $2 and writable by no one else" >&2
      return 1
    fi
  done
}

# Fails, naming each entry, when anything under the given directories is not owned by root or is writable by group or
# others (a link only needs root as its owner).
check_root_tree() {
  found=$(find "$@" \( ! -user 0 -o \( ! -type l \( -perm -g+w -o -perm -o+w \) \) \) -print)
  [ -z "$found" ] || { printf 'not owned by root alone:\n%s\n' "$found" >&2; return 1; }
}
