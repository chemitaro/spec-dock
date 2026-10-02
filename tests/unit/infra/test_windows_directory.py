"""Win32 API substitutions exercise handle anchoring, not native FS support."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.windows_handles import WindowsDirectory

if TYPE_CHECKING:
    from pathlib import Path


class DirectoryKernel:
    """A parent path is replaced while the original open object stays alive."""

    def __init__(self, target: Path) -> None:
        self.target = target
        self.objects: dict[int, tuple[Path, bool]] = {}
        self.replaced = False
        self.closed: list[int] = []

    def _open(self, path: Path, original: bool) -> int:
        handle = len(self.objects) + 1
        self.objects[handle] = path, original
        if path == self.target.parent:
            self.replaced = True
        return handle

    def CreateFileW(self, name, access, share, security, disposition, flags, template):
        path = type(self.target)(name)
        return self._open(path, not (self.replaced and path == self.target))

    def NtOpenFile(self, result, access, attributes, status, share, options):
        attributes = attributes._obj
        parent, original = self.objects[attributes.RootDirectory]
        name = attributes.ObjectName.contents
        component = ctypes.string_at(name.Buffer, name.Length).decode("utf-16-le")
        result._obj.value = self._open(parent / component, original)
        return 0

    def RtlNtStatusToDosError(self, status):
        return 5

    def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
        if kind == 9:
            buffer._obj.FileAttributes = 0x10
        elif kind == 18:
            path, original = self.objects[handle]
            buffer._obj.VolumeSerialNumber = 123
            identifier = "33" if path != self.target else "11" if original else "22"
            buffer._obj.FileId[:] = bytes.fromhex(identifier * 16)
        else:
            raise AssertionError(f"unexpected file information class: {kind}")
        return 1

    def CloseHandle(self, handle):
        self.closed.append(handle)
        return 1


@pytest.mark.parametrize("components", [("parent", "child"), ("親📦", "子")])
def test_parent_path_replacement_cannot_redirect_the_held_child_identity(
    tmp_path: Path, components: tuple[str, str]
) -> None:
    target = tmp_path / components[0] / components[1]
    api = DirectoryKernel(target)
    with WindowsDirectory(target, kernel32=api) as held:
        assert api.replaced
        assert held.identity.file_id == "11111111111111111111111111111111"
    assert set(api.closed) == set(api.objects)


@pytest.mark.parametrize("attributes", [0x410, 0x80])
def test_redirected_or_non_directory_child_is_rejected_and_closed(tmp_path: Path, attributes: int) -> None:
    class UnsafeKernel(DirectoryKernel):
        def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
            result = super().GetFileInformationByHandleEx(handle, kind, buffer, size)
            if kind == 9 and self.objects[handle][0] == self.target:
                buffer._obj.FileAttributes = attributes
            return result

    api = UnsafeKernel(tmp_path / "parent" / "child")
    with (
        pytest.raises(ValueError, match="redirected or is not a directory"),
        WindowsDirectory(api.target, kernel32=api),
    ):
        pytest.fail("unsafe child was accepted")
    assert set(api.closed) == set(api.objects)


def test_unexpected_pending_open_does_not_leave_an_unowned_handle(tmp_path: Path) -> None:
    class PendingKernel(DirectoryKernel):
        def NtOpenFile(self, *arguments):
            super().NtOpenFile(*arguments)
            return 0x103  # STATUS_PENDING is not a completed synchronous open.

    api = PendingKernel(tmp_path / "parent" / "child")
    with pytest.raises(OSError), WindowsDirectory(api.target, kernel32=api):
        pytest.fail("pending open was treated as a completed directory")
    assert set(api.closed) == set(api.objects)
