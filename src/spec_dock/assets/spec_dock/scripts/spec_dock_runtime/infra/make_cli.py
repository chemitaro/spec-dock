_MISSING_INIT_TARGET_FRAGMENTS = (
    "no rule to make target 'init'",
    "no rule to make target `init'",
    "no rule to make target init",
    "no targets specified and no makefile found",
    "no makefile found",
)


def is_missing_init_target(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(fragment in lowered for fragment in _MISSING_INIT_TARGET_FRAGMENTS)
