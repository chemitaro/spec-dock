"""Minimal non-inheritable Win32 handles; no ACL or namespace fallback."""

from __future__ import annotations

import ctypes
import math
import sys
import time
from types import SimpleNamespace
from typing import TYPE_CHECKING, Protocol, cast

from spec_dock.runtime.domain.work_target import PhysicalIdentity

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class MutexAPI(Protocol):
    def CreateMutexW(self, security: object, owned: int, name: str) -> int: ...
    def WaitForSingleObject(self, handle: int, milliseconds: int) -> int: ...
    def ReleaseMutex(self, handle: int) -> int: ...
    def CloseHandle(self, handle: int) -> int: ...


def _native_mutex_api() -> MutexAPI:
    if sys.platform != "win32":
        raise NotImplementedError("Win32 mutex API is not available")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel.WaitForSingleObject.restype = ctypes.c_uint32
    kernel.ReleaseMutex.argtypes = [ctypes.c_void_p]
    kernel.ReleaseMutex.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    return cast("MutexAPI", kernel)


def _api_error(operation: str) -> OSError:
    if sys.platform == "win32":
        return cast("OSError", ctypes.WinError(ctypes.get_last_error()))
    return OSError(f"{operation} failed")


class DirectoryAPI(Protocol):
    def CreateFileW(
        self, name: str, access: int, share: int, security: object, disposition: int, flags: int, template: object
    ) -> int: ...
    def NtOpenFile(
        self, result: object, access: int, attributes: object, status: object, share: int, options: int
    ) -> int: ...
    def RtlNtStatusToDosError(self, status: int) -> int: ...
    def GetFileInformationByHandleEx(self, handle: int, kind: int, buffer: object, size: int) -> int: ...
    def CloseHandle(self, handle: int) -> int: ...


class _FileAttributeTagInfo(ctypes.Structure):
    _fields_ = [("FileAttributes", ctypes.c_uint32), ("ReparseTag", ctypes.c_uint32)]


class _FileIdInfo(ctypes.Structure):
    _fields_ = [("VolumeSerialNumber", ctypes.c_uint64), ("FileId", ctypes.c_ubyte * 16)]


class _UnicodeString(ctypes.Structure):
    _fields_ = [
        ("Length", ctypes.c_uint16),
        ("MaximumLength", ctypes.c_uint16),
        ("Buffer", ctypes.POINTER(ctypes.c_uint16)),
    ]


class _ObjectAttributes(ctypes.Structure):
    _fields_ = [
        ("Length", ctypes.c_uint32),
        ("RootDirectory", ctypes.c_void_p),
        ("ObjectName", ctypes.POINTER(_UnicodeString)),
        ("Attributes", ctypes.c_uint32),
        ("SecurityDescriptor", ctypes.c_void_p),
        ("SecurityQualityOfService", ctypes.c_void_p),
    ]


class _IoStatusValue(ctypes.Union):
    _fields_ = (("Status", ctypes.c_int32), ("Pointer", ctypes.c_void_p))


class _IoStatusBlock(ctypes.Structure):
    _fields_ = [("Value", _IoStatusValue), ("Information", ctypes.c_size_t)]


def _native_directory_api() -> DirectoryAPI:
    if sys.platform != "win32":
        raise NotImplementedError("Win32 directory API is not available")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.GetFileInformationByHandleEx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    kernel.GetFileInformationByHandleEx.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    native = ctypes.WinDLL("ntdll")
    native.NtOpenFile.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_uint32,
        ctypes.POINTER(_ObjectAttributes),
        ctypes.POINTER(_IoStatusBlock),
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    native.NtOpenFile.restype = ctypes.c_int32
    native.RtlNtStatusToDosError.argtypes = [ctypes.c_int32]
    native.RtlNtStatusToDosError.restype = ctypes.c_uint32
    return cast(
        "DirectoryAPI",
        SimpleNamespace(
            CreateFileW=kernel.CreateFileW,
            NtOpenFile=native.NtOpenFile,
            RtlNtStatusToDosError=native.RtlNtStatusToDosError,
            GetFileInformationByHandleEx=kernel.GetFileInformationByHandleEx,
            CloseHandle=kernel.CloseHandle,
        ),
    )


def _open_child_directory(api: DirectoryAPI, parent: int, name: str) -> int:
    if not name or name in (".", "..") or any(character in name for character in ("/", "\\", "\0", ":")):
        raise ValueError("physical directory name must be a single path component")
    encoded = name.encode("utf-16-le")
    if len(encoded) > 65532:
        raise ValueError("physical directory name is too long")
    buffer = ctypes.create_string_buffer(encoded + b"\0\0")
    string = _UnicodeString(len(encoded), len(encoded) + 2, ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint16)))
    attributes = _ObjectAttributes(ctypes.sizeof(_ObjectAttributes), parent, ctypes.pointer(string), 0x40, None, None)
    result = ctypes.c_void_p()
    io_status = _IoStatusBlock()
    # FILE_READ_ATTRIBUTES | SYNCHRONIZE; directory, synchronous, no reparse traversal.
    status = api.NtOpenFile(
        ctypes.byref(result), 0x100080, ctypes.byref(attributes), ctypes.byref(io_status), 7, 0x200021
    )
    if status != 0:
        if (
            ctypes.c_int32(status).value >= 0
            and result.value
            and result.value != ctypes.c_void_p(-1).value
            and not api.CloseHandle(result.value)
        ):
            raise _api_error("CloseHandle")
        if sys.platform == "win32":
            raise ctypes.WinError(api.RtlNtStatusToDosError(status))
        raise OSError(f"NtOpenFile failed: NTSTATUS 0x{status & 0xFFFFFFFF:08x}")
    if not result.value or result.value == ctypes.c_void_p(-1).value:
        raise OSError("NtOpenFile returned an invalid directory handle")
    return result.value


class WindowsDirectory:
    def __init__(self, path: Path, *, kernel32: DirectoryAPI | None = None) -> None:
        self.path = path.absolute()
        self._api = kernel32
        self._handles: list[int] = []

    def __enter__(self) -> WindowsDirectory:
        if self._handles:
            raise RuntimeError("physical directory handle is already open")
        if ".." in self.path.parts:
            raise ValueError("physical directory path contains traversal")
        api = self._api or _native_directory_api()
        self._api = api
        try:
            for component in (*reversed(self.path.parents), self.path):
                if self._handles:
                    handle = _open_child_directory(api, self._handles[-1], component.name)
                else:
                    handle = api.CreateFileW(str(component), 0x80, 7, None, 3, 0x02200000, None)
                if not handle or handle == ctypes.c_void_p(-1).value:
                    raise _api_error("CreateFileW")
                self._handles.append(handle)
                attributes = _FileAttributeTagInfo()
                if not api.GetFileInformationByHandleEx(handle, 9, ctypes.byref(attributes), ctypes.sizeof(attributes)):
                    raise _api_error("GetFileInformationByHandleEx")
                if attributes.FileAttributes & 0x400 or not attributes.FileAttributes & 0x10:
                    raise ValueError("physical directory is redirected or is not a directory")
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    @property
    def identity(self) -> PhysicalIdentity:
        if not self._handles or self._api is None:
            raise RuntimeError("physical directory handle is not open")
        observed = _FileIdInfo()
        if not self._api.GetFileInformationByHandleEx(
            self._handles[-1], 18, ctypes.byref(observed), ctypes.sizeof(observed)
        ):
            raise _api_error("GetFileInformationByHandleEx")
        return PhysicalIdentity("windows", str(observed.VolumeSerialNumber), bytes(observed.FileId).hex())

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        first_error: OSError | None = None
        assert self._api is not None or not self._handles
        while self._handles:
            handle = self._handles.pop()
            assert self._api is not None
            if not self._api.CloseHandle(handle) and first_error is None:
                first_error = _api_error("CloseHandle")
        if first_error is not None:
            raise first_error


class WindowsMutex:
    def __init__(self, name: str, *, timeout: float, kernel32: MutexAPI | None = None) -> None:
        if not name.startswith("Global\\SpecDock.Start.v1."):
            raise ValueError("Start mutex must use its Global namespace")
        if not math.isfinite(timeout) or not 0 <= timeout <= 300:
            raise ValueError("Start lock timeout must be finite and between 0 and 300 seconds")
        self.name = name
        self.timeout = timeout
        self._api = kernel32
        self._handle: int | None = None
        self.abandoned = False

    def __enter__(self) -> WindowsMutex:
        if self._handle is not None:
            raise RuntimeError("Start mutex is already held")
        api = self._api or _native_mutex_api()
        handle = api.CreateMutexW(None, 0, self.name)
        if not handle:
            raise _api_error("CreateMutexW")
        deadline = time.monotonic() + self.timeout
        try:
            while True:
                remaining = max(0.0, deadline - time.monotonic())
                outcome = api.WaitForSingleObject(handle, math.ceil(remaining * 1000))
                if outcome in (0, 128):
                    self.abandoned = outcome == 128
                    break
                if outcome == 258:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("another work start holds the clone lock")
                    continue
                raise _api_error("WaitForSingleObject")
        except BaseException:
            api.CloseHandle(handle)
            raise
        self._api, self._handle = api, handle
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        if self._handle is not None:
            handle, self._handle = self._handle, None
            assert self._api is not None
            try:
                if not self._api.ReleaseMutex(handle):
                    raise _api_error("ReleaseMutex")
            finally:
                if not self._api.CloseHandle(handle):
                    raise _api_error("CloseHandle")
