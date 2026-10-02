"""Win32 boundary contract; native process coverage remains required on Windows."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator


class KernelMutexAPI:
    """Substitute the external kernel32 API, without emulating SpecDock objects."""

    def __init__(self, waits: tuple[int, ...] = (0,)) -> None:
        self.waits: Iterator[int] = iter(waits)
        self.events: list[tuple[object, ...]] = []

    def CreateMutexW(self, security: object, owned: int, name: str) -> int:
        self.events.append(("create", security, owned, name))
        return 42

    def WaitForSingleObject(self, handle: int, milliseconds: int) -> int:
        self.events.append(("wait", handle, milliseconds))
        return next(self.waits)

    def ReleaseMutex(self, handle: int) -> int:
        self.events.append(("release", handle))
        return 1

    def CloseHandle(self, handle: int) -> int:
        self.events.append(("close", handle))
        return 1


def test_abandoned_mutex_is_acquired_and_released_without_recovery() -> None:
    from spec_dock.runtime.infra.windows_handles import WindowsMutex

    api = KernelMutexAPI((128,))
    with WindowsMutex("Global\\SpecDock.Start.v1.test", timeout=0, kernel32=api) as held:
        assert held.abandoned is True
    assert api.events == [
        ("create", None, 0, "Global\\SpecDock.Start.v1.test"),
        ("wait", 42, 0),
        ("release", 42),
        ("close", 42),
    ]


@pytest.mark.parametrize("outcome", [258, 0xFFFFFFFF])
def test_failed_acquisition_closes_handle_without_releasing_unowned_mutex(outcome: int) -> None:
    from spec_dock.runtime.infra.windows_handles import WindowsMutex

    api = KernelMutexAPI((outcome,))
    with (
        pytest.raises(TimeoutError if outcome == 258 else OSError),
        WindowsMutex("Global\\SpecDock.Start.v1.test", timeout=0, kernel32=api),
    ):
        pytest.fail("unowned mutex entered")
    assert api.events[-1] == ("close", 42)
    assert not any(event[0] == "release" for event in api.events)


def test_directory_identity_uses_win32_volume_and_128_bit_file_id(tmp_path) -> None:
    from spec_dock.runtime.infra.windows_handles import WindowsDirectory

    class KernelDirectoryAPI:
        def __init__(self) -> None:
            self.opened: list[tuple[object, ...]] = []
            self.relative_opened: list[tuple[object, ...]] = []
            self.closed: list[int] = []

        def CreateFileW(self, *args):
            self.opened.append(args)
            return len(self.opened)

        def NtOpenFile(self, result, access, attributes, status, share, options):
            attributes = attributes._obj
            name = attributes.ObjectName.contents
            component = ctypes.string_at(name.Buffer, name.Length).decode("utf-16-le")
            self.relative_opened.append((
                attributes.RootDirectory,
                component,
                attributes.Attributes,
                attributes.SecurityDescriptor,
                access,
                share,
                options,
            ))
            result._obj.value = len(self.opened) + len(self.relative_opened)
            return 0

        def RtlNtStatusToDosError(self, status):
            pytest.fail(f"unexpected NTSTATUS error: {status}")

        def GetFileInformationByHandleEx(self, handle, kind, buffer, size):
            if kind == 9:
                buffer._obj.FileAttributes = 0x10
                buffer._obj.ReparseTag = 0
            elif kind == 18:
                buffer._obj.VolumeSerialNumber = 123
                buffer._obj.FileId[:] = bytes.fromhex("00112233445566778899aabbccddeeff")
            else:
                pytest.fail(f"unexpected file information class: {kind}")
            return 1

        def CloseHandle(self, handle):
            self.closed.append(handle)
            return 1

    api = KernelDirectoryAPI()
    with WindowsDirectory(tmp_path, kernel32=api) as held:
        assert held.identity.platform == "windows"
        assert held.identity.device == "123"
        assert held.identity.file_id == "00112233445566778899aabbccddeeff"
        assert len(api.opened) == 1  # Only the filesystem anchor uses an absolute Win32 name.
        assert all(args[1:] == (0x80, 7, None, 3, 0x02200000, None) for args in api.opened)
        assert all(args[2:] == (0x40, None, 0x100080, 7, 0x200021) for args in api.relative_opened)
    assert sorted(api.closed) == list(range(1, len(api.opened) + len(api.relative_opened) + 1))
