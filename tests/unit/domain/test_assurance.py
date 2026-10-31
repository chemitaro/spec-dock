"""iss-00474 AC-02/AC-03: the assurance arguments and the reason as the inside of a CUE string."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.assurance import (
    ASSURANCE_LEVELS,
    LEVEL_MARKER,
    REASON_MARKER,
    Assurance,
    assurance_replacements,
    cue_string_body,
    parse_assurance,
)
from tests.support.cue import cue_executable

if TYPE_CHECKING:
    from pathlib import Path

TRICKY_REASONS = [
    "既定の理由",
    'He said "fine" \\ and left',
    "一行目\n二行目\tタブ\r\n終わり",
    "\\(not.interpolated) and \\n stays literal",
    "制御文字\x00\x01\x07\x08\x0b\x0c\x1b\x1fと\x7fを含む",
    "区切り\u2028と\u2029、BOM\ufeffの途中",
    "\ufeff先頭のBOM",
    "絵文字 😀 と 𠮷",
    "印 {{ASSURANCE_LEVEL}} {{ASSURANCE_REASON}} YYYY-MM-DD <ISS_ID> ](../docs/x.md)",
    "-urgent",
]


def _cue_read(tmp_path: Path, body: str) -> object:
    source = tmp_path / "value.cue"
    source.write_text(f'package spec\nreason: "{body}"\n', encoding="utf-8")
    completed = subprocess.run(
        [cue_executable(), "export", "--out", "json", str(source)], capture_output=True, text=True, check=False
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)["reason"]


def test_the_levels_are_the_four_names_in_rank_order() -> None:
    assert ASSURANCE_LEVELS == ("light", "standard", "strict", "critical")


@pytest.mark.parametrize("reason", TRICKY_REASONS)
def test_the_body_reads_back_as_the_same_text_with_the_real_cue(tmp_path: Path, reason: str) -> None:
    body = cue_string_body(reason)
    assert "\n" not in body and "\ufeff" not in body
    assert _cue_read(tmp_path, body) == reason


@pytest.mark.parametrize("level", ASSURANCE_LEVELS)
def test_parse_keeps_the_level_and_strips_the_reason(level: str) -> None:
    assert parse_assurance(level, "  影響が広い  \n") == Assurance(level, "影響が広い")


@pytest.mark.parametrize(
    ("level", "reason", "argument"),
    [
        (None, "理由", "--assurance"),
        ("standard", None, "--assurance-reason"),
        (None, None, "--assurance"),
        ("standard", "", "--assurance-reason"),
        ("standard", " \t\n", "--assurance-reason"),
        ("standard", "　　", "--assurance-reason"),  # full-width spaces only
        ("standard", "\x1c\x85", "--assurance-reason"),  # what the type's #Text also treats as blank
        ("standard", "壊れた\udce3文字", "--assurance-reason"),  # not encodable as UTF-8
        ("medium", "理由", "--assurance"),
    ],
)
def test_parse_refuses_a_missing_blank_or_unusable_value(level: str | None, reason: str | None, argument: str) -> None:
    with pytest.raises(ValueError, match="--assurance") as raised:
        parse_assurance(level, reason)
    assert raised.value.args[1] == argument


def test_the_replacements_fill_both_markers_with_the_escaped_reason() -> None:
    replacements = assurance_replacements(Assurance("strict", 'a "b"\nc'))
    assert replacements == {LEVEL_MARKER: "strict", REASON_MARKER: 'a \\"b\\"\\nc'}
