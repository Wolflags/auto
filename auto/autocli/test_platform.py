"""Tests for the autocli.platform helpers"""

import os

from autocli import platform


def test_auto_dir_uses_native_join():
    """auto_dir joins under ~/.auto with the native separator"""
    expected = os.path.join(os.path.expanduser("~"), ".auto", "k3s", "pv.yaml")
    assert platform.auto_dir("k3s", "pv.yaml") == expected


def test_posix_path_is_forward_slashed():
    """posix_path returns forward slashes for tool flags on every platform"""
    result = platform.posix_path(os.path.join("foo", "bar", "baz.yaml"))
    assert "\\" not in result
    assert result.endswith("foo/bar/baz.yaml")


def test_to_mount_path_has_no_backslashes(tmp_path):
    """to_mount_path forward-slashes the host path so only a drive-letter ':' remains"""
    result = platform.to_mount_path(str(tmp_path))
    assert "\\" not in result


def test_hosts_path_windows(monkeypatch):
    """Windows hosts path is built from %SystemRoot% + System32\\drivers\\etc\\hosts"""
    monkeypatch.setattr(platform, "IS_WINDOWS", True)
    monkeypatch.setenv("SystemRoot", r"C:\Windows")
    # Build the expected value with the same os.path.join so the separator matches
    # whatever OS runs the test (CI runs this on Linux/macOS too, where join uses '/').
    expected = os.path.join(r"C:\Windows", "System32", "drivers", "etc", "hosts")
    assert platform.hosts_path() == expected


def test_hosts_path_posix(monkeypatch):
    """POSIX hosts path is /etc/hosts"""
    monkeypatch.setattr(platform, "IS_WINDOWS", False)
    assert platform.hosts_path() == "/etc/hosts"


def test_read_hosts_missing_returns_empty(monkeypatch):
    """read_hosts never raises when the file is unreadable/absent"""
    monkeypatch.setattr(
        platform, "hosts_path", lambda: os.path.join("no", "such", "hosts")
    )
    assert platform.read_hosts() == ""


def test_k3d_bin_uses_which_when_present(monkeypatch):
    """k3d_bin returns the PATH-resolved binary when found"""
    monkeypatch.setattr(platform.shutil, "which", lambda name: "/somewhere/k3d")
    assert platform.k3d_bin() == "/somewhere/k3d"


def test_k3d_bin_falls_back_to_bare_name(monkeypatch):
    """k3d_bin falls back to the bare name so subprocess does its own PATH lookup"""
    monkeypatch.setattr(platform.shutil, "which", lambda name: None)
    # Skip the POSIX /usr/local/bin fallback so we exercise the bare-name return
    monkeypatch.setattr(platform, "IS_WINDOWS", True)
    assert platform.k3d_bin() == "k3d"
