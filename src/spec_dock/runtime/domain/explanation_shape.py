"""The thin explanation shape of contract K5 (epic-00425), as `scope check` judges explanation.html (iss-00473).

A thin explanation holds exactly one Markdown block `<script type="text/markdown" id="ds-source">` whose front
matter names a `title`, and loads the shared design system from `../../../design-system/` (ds.css and ds.js).
The skeleton marker left inside the Markdown means the author has not rewritten the skeleton yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Final

SKELETON_MARKER: Final = "<!-- spec-dock:explanation-skeleton -->"
DESIGN_SYSTEM_CSS: Final = "../../../design-system/ds.css"
DESIGN_SYSTEM_JS: Final = "../../../design-system/ds.js"


@dataclass(frozen=True)
class ExplanationShape:
    skeleton: bool
    problems: tuple[str, ...]


class _Reader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []
        self.stylesheet = False
        self.script = False
        self._in_source = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "script":
            if values.get("type") == "text/markdown" and values.get("id") == "ds-source":
                self.sources.append("")
                self._in_source = True
            if values.get("src") == DESIGN_SYSTEM_JS:
                self.script = True
        elif (
            tag == "link" and "stylesheet" in values.get("rel", "").split() and values.get("href") == DESIGN_SYSTEM_CSS
        ):
            self.stylesheet = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_source = False

    def handle_data(self, data: str) -> None:
        if self._in_source:
            self.sources[-1] += data


def inspect_explanation(text: str) -> ExplanationShape:
    """Whether the explanation is still the skeleton, and every way its shape is broken (empty when it is not)."""
    reader = _Reader()
    reader.feed(text)
    reader.close()
    problems: list[str] = []
    if len(reader.sources) != 1:
        problems.append(
            f'needs exactly one <script type="text/markdown" id="ds-source"> block; found {len(reader.sources)}'
        )
    elif not _has_title(reader.sources[0]):
        problems.append("the Markdown in ds-source must start with front matter (---) that has a non-blank title:")
    if not reader.stylesheet:
        problems.append(f'needs <link rel="stylesheet" href="{DESIGN_SYSTEM_CSS}"> to load ds.css')
    if not reader.script:
        problems.append(f'needs <script src="{DESIGN_SYSTEM_JS}"> to load ds.js')
    markdown = reader.sources[0] if len(reader.sources) == 1 else text
    return ExplanationShape(SKELETON_MARKER in markdown, tuple(problems))


def _has_title(markdown: str) -> bool:
    lines = markdown.lstrip().splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        key, separator, value = line.partition(":")
        if separator and key.strip() == "title" and value.strip():
            return True
    return False
