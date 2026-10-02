"""External Win32 API substitutions; native filesystem acceptance is separate."""

from __future__ import annotations

import ctypes
import json
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra import json_store, windows_handles

if TYPE_CHECKING:
    from pathlib import Path


class FileKernel:
    """The held parent survives replacement of its path before the leaf opens."""

    def __init__(self, path: Path, payload: bytes) -> None:
        self.path = path
        self.payload = payload
        self.objects: dict[int, tuple[Path, bool, bool]] = {}
        self.positions: dict[int, int] = {}
        self.closed: list[int] = []
        self.replaced = False
        self.file_id = bytes.fromhex("00112233445566778899aabbccddeeff")
        self.leaf_opens: list[tuple[int, int, int, int]] = []

    def _open(self, path: Path, original: bool, file: bool) -> int:
        handle = len(self.objects) + 1
        self.objects[handle] = path, original, file
        self.positions[handle] = 0
        if path == self.path.parent:
            self.replaced = True
        return handle

    def CreateFileW(self, name, access, share, security, disposition, flags, template):
        path = type(self.path)(name)
        return self._open(path, not self.replaced, path == self.path)

    def NtOpenFile(self, result, access, attributes, status, share, options):
        attributes = attributes._obj
        parent, original, _ = self.objects[attributes.RootDirectory]
        name = attributes.ObjectName.contents
        component = ctypes.string_at(name.Buffer, name.Length).decode("utf-16-le")
        if options & 0x40:
            self.leaf_opens.append((access, share, options, attributes.Attributes))
        result._obj.value = self._open(parent / component, original, bool(options & 0x40))
        return 0

    def RtlNtStatusToDosError(self, status):
        return {0xC000000F: 2, 0xC0000034: 2, 0xC000003A: 3}.get(status & 0xFFFFFFFF, 5)

    def GetFileType(self, handle):
        return 1

    def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
        _, _, file = self.objects[handle]
        if kind == 9:
            buffer._obj.FileAttributes = 0x80 if file else 0x10
        elif kind == 1:
            buffer._obj.NumberOfLinks = 1
            buffer._obj.Directory = not file
        elif kind == 18:
            buffer._obj.VolumeSerialNumber = 2**63 + 17
            buffer._obj.FileId[:] = self.file_id
        else:
            raise AssertionError(f"unexpected file information class: {kind}")
        return 1

    def ReadFile(self, handle, buffer, size, count, overlapped):
        _, original, file = self.objects[handle]
        assert file and overlapped is None
        payload = self.payload if original else b'{"redirected":true}'
        start = self.positions[handle]
        data = payload[start : start + size]
        ctypes.memmove(buffer, data, len(data))
        count._obj.value = len(data)
        self.positions[handle] += len(data)
        return 1

    def CloseHandle(self, handle):
        self.closed.append(handle)
        return 1


@pytest.mark.parametrize("characters", ["日本語", "日" * 50000])
def test_windows_json_read_uses_held_parent_exact_bytes_and_full_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, characters: str
) -> None:
    path = tmp_path / "親📦" / "metadata.json"
    path.parent.mkdir()
    payload = ('  {"title": "' + characters + '", "schema_version": 3}\n').encode()
    api = FileKernel(path, payload)
    monkeypatch.setattr(json_store, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(windows_handles, "_native_directory_api", lambda: api)

    loaded = json_store.read_guarded_json_bytes(path)

    assert api.replaced
    assert loaded == (json.loads(payload), payload, (2**63 + 17, int.from_bytes(api.file_id, "little")))
    assert api.leaf_opens == [(0x100081, 7, 0x200060, 0x40)]
    assert sorted(api.closed) == sorted(api.objects)


@pytest.mark.parametrize(
    "unsafe", ["reparse", "directory", "hardlink", "no_link", "standard_directory", "pipe", "device"]
)
def test_unsafe_windows_json_leaf_is_rejected_before_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unsafe: str
) -> None:
    class UnsafeKernel(FileKernel):
        def GetFileType(self, handle):
            return 3 if unsafe == "pipe" else 2 if unsafe == "device" else 1

        def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
            result = super().GetFileInformationByHandleEx(handle, kind, buffer, size)
            if self.objects[handle][2]:
                if kind == 9 and unsafe in ("reparse", "directory"):
                    buffer._obj.FileAttributes = 0x400 if unsafe == "reparse" else 0x10
                elif kind == 1:
                    buffer._obj.NumberOfLinks = 2 if unsafe == "hardlink" else 0 if unsafe == "no_link" else 1
                    buffer._obj.Directory = unsafe == "standard_directory"
            return result

    api = UnsafeKernel(tmp_path / "metadata.json", b"{}")
    monkeypatch.setattr(json_store, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(windows_handles, "_native_directory_api", lambda: api)
    with pytest.raises(ValueError, match="single-link regular"):
        json_store.read_guarded_json_bytes(api.path)
    assert all(position == 0 for position in api.positions.values())
    assert sorted(api.closed) == sorted(api.objects)


@pytest.mark.parametrize("status", [0xC000000F, 0xC0000034, 0xC000003A, 0xC0000022])
@pytest.mark.parametrize("location", ["leaf", "parent"])
def test_only_missing_windows_json_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: int, location: str
) -> None:
    class FailedOpenKernel(FileKernel):
        def NtOpenFile(self, result, access, attributes, io_status, share, options):
            opened = attributes._obj
            parent = self.objects[opened.RootDirectory][0]
            name = opened.ObjectName.contents
            component = ctypes.string_at(name.Buffer, name.Length).decode("utf-16-le")
            if (location == "leaf" and options & 0x40) or (
                location == "parent" and parent / component == self.path.parent
            ):
                return ctypes.c_int32(status).value
            return super().NtOpenFile(result, access, attributes, io_status, share, options)

    api = FailedOpenKernel(tmp_path / "metadata.json", b"{}")
    monkeypatch.setattr(json_store, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(windows_handles, "_native_directory_api", lambda: api)
    if status == 0xC0000022:
        with pytest.raises(OSError) as failed:
            json_store.read_guarded_json_bytes(api.path)
        assert not isinstance(failed.value, FileNotFoundError)
    else:
        assert json_store.read_guarded_json_bytes(api.path) is None
    assert sorted(api.closed) == sorted(api.objects)


@pytest.mark.parametrize("payload", [b"{", b"\xff"])
def test_invalid_windows_json_closes_handles_without_becoming_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: bytes
) -> None:
    api = FileKernel(tmp_path / "metadata.json", payload)
    monkeypatch.setattr(json_store, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(windows_handles, "_native_directory_api", lambda: api)
    with pytest.raises((json.JSONDecodeError, UnicodeDecodeError)):
        json_store.read_guarded_json_bytes(api.path)
    assert sorted(api.closed) == sorted(api.objects)


@pytest.mark.parametrize("failure", ["pending_open", "read", "invalid_count", "file_info"])
def test_failed_windows_json_io_does_not_leak_handles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    class FailedKernel(FileKernel):
        def NtOpenFile(self, result, access, attributes, status, share, options):
            completed = super().NtOpenFile(result, access, attributes, status, share, options)
            return 0x103 if failure == "pending_open" and options & 0x40 else completed

        def ReadFile(self, handle, buffer, size, count, overlapped):
            if failure == "read":
                if sys.platform == "win32":
                    ctypes.set_last_error(5)
                return 0
            if failure == "invalid_count":
                count._obj.value = size + 1
                return 1
            return super().ReadFile(handle, buffer, size, count, overlapped)

        def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
            if failure == "file_info" and kind == 18 and self.objects[handle][2]:
                if sys.platform == "win32":
                    ctypes.set_last_error(5)
                return 0
            return super().GetFileInformationByHandleEx(handle, kind, buffer, size)

    api = FailedKernel(tmp_path / "metadata.json", b"{}")
    monkeypatch.setattr(json_store, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(windows_handles, "_native_directory_api", lambda: api)
    with pytest.raises(OSError):
        json_store.read_guarded_json_bytes(api.path)
    assert sorted(api.closed) == sorted(api.objects)


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows reader boundary")
def test_native_windows_json_keeps_exact_bytes_and_rejects_hardlink(tmp_path: Path) -> None:
    import os

    path = tmp_path / "metadata.json"
    payload = b' {"schema_version":3}\n'
    path.write_bytes(payload)
    loaded = json_store.read_guarded_json_bytes(path)
    assert loaded is not None and loaded[0] == json.loads(payload) and loaded[1] == payload
    assert loaded[2][0] >= 0 and loaded[2][1] >= 0
    os.link(path, tmp_path / "alias.json")
    with pytest.raises(ValueError, match="single-link regular"):
        json_store.read_guarded_json_bytes(path)


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows held parent boundary")
def test_native_windows_json_parent_replacement_keeps_original_leaf(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    parent.mkdir()
    payload = b'{"original":true}'
    (parent / "metadata.json").write_bytes(payload)
    with windows_handles.WindowsDirectory(parent) as held:
        parent.rename(tmp_path / "old")
        parent.mkdir()
        (parent / "metadata.json").write_bytes(b'{"redirected":true}')
        captured = held.read_file_bytes("metadata.json")
        assert captured is not None and captured[0] == payload
