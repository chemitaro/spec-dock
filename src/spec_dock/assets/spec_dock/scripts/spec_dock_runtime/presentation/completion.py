"""Shell completion definitions derived from the command catalog."""

from __future__ import annotations

from spec_dock_runtime.cli.catalog import LEAF_PATHS


def _children() -> dict[str, tuple[str, ...]]:
    children: dict[str, set[str]] = {}
    for leaf in LEAF_PATHS:
        parts = leaf.split()
        for index, word in enumerate(parts):
            prefix = " ".join(parts[:index])
            children.setdefault(prefix, set()).add(word)
    return {prefix: tuple(sorted(words)) for prefix, words in children.items()}


def completion_script(shell: str) -> str:
    children = _children()
    if shell == "bash":
        lines = [
            "_spec_dock_complete() {",
            "  local path='' choices='' i",
            '  for ((i=1; i<COMP_CWORD; i++)); do path="${path:+$path }${COMP_WORDS[i]}"; done',
            '  case "$path" in',
        ]
        lines.extend(f'    "{prefix}") choices="{" ".join(words)}";;' for prefix, words in children.items())
        lines.extend([
            "  esac",
            '  COMPREPLY=( $(compgen -W "$choices" -- "${COMP_WORDS[COMP_CWORD]}") )',
            "}",
            "complete -F _spec_dock_complete spec-dock",
        ])
    elif shell == "zsh":
        lines = [
            "#compdef spec-dock",
            "_spec_dock() {",
            "  local path='' i",
            "  local -a choices",
            '  for ((i=2; i<CURRENT; i++)); do path="${path:+$path }${words[i]}"; done',
            '  case "$path" in',
        ]
        lines.extend(f'    "{prefix}") choices=({" ".join(words)});;' for prefix, words in children.items())
        lines.extend(["  esac", "  _describe 'spec-dock command' choices", "}", "compdef _spec_dock spec-dock"])
    elif shell == "fish":
        lines = [
            "function __spec_dock_subcommands",
            "  set -l tokens (commandline -opc)",
            "  set -e tokens[1]",
            "  set -l path (string join ' ' -- $tokens)",
            '  switch "$path"',
        ]
        for prefix, words in children.items():
            lines.append(f'    case "{prefix}"')
            lines.extend(f"      echo {word}" for word in words)
        lines.extend(["  end", "end", "complete -c spec-dock -f -a '(__spec_dock_subcommands)'"])
    else:
        raise ValueError(f"unsupported completion shell: {shell}")
    return "\n".join(lines) + "\n"
