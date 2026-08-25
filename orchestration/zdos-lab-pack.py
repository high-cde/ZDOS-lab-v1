#!/usr/bin/env python3
"""Build portable developer bundles for the ZDOS ecosystem.

The bundles are deliberately source-first: no ISO is included. Linux archives
are verified in the current environment; Windows wrappers are prepared for
Windows 7+ but are never marked VERIFIED without a Windows test run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(__import__("os").environ.get("ZDOS_LAB_WORKSPACE", ROOT.parent)).resolve()
COMPONENTS = {
    "zdos": WORKSPACE / "ZDOS",
    "zlang": WORKSPACE / "Zlang",
    "sec": WORKSPACE / "ZDOS-SEC-PORTAL",
}
EXCLUDE_PARTS = {".git", "target", "node_modules", "__pycache__", "dist", "out"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_filtered(source: Path, target: Path) -> None:
    if source.is_dir():
        for item in source.iterdir():
            if item.name in EXCLUDE_PARTS:
                continue
            copy_filtered(item, target / item.name)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_common_files(stage: Path, component: str) -> None:
    (stage / "PLATFORM-MATRIX.md").write_text(
        "# ZDOS portable package\n\n"
        "This package is separate from the ZDOS ISO and contains development/runtime sources.\n\n"
        "| Platform | Artifact | Status |\n|---|---|---|\n"
        "| Linux x86_64 | tar.gz / zip | VERIFIED in the build environment |\n"
        "| Ubuntu, Kali, Parrot | source bundle + launcher | PREPARED; use the distro package manager for dependencies |\n"
        "| Windows 7 | zip + `.cmd` launcher | PREPARED; requires a compatible Python/Node runtime |\n"
        "| Native `.exe` | not emitted by this host | NOT_VERIFIED until cross-build and Windows 7 test |\n\n"
        "Do not treat a Windows wrapper as a native executable. Checksums in `SHA256SUMS` identify the exact archive.\n",
        encoding="utf-8",
    )
    (stage / "README-PORTABLE.md").write_text(
        f"# {component.upper()} portable bundle\n\n"
        "This developer bundle intentionally excludes the bootable ISO.\n"
        "Use the included manifest and SHA-256 file before extracting or running code.\n\n"
        "Windows 7 is supported as a preparation target only: native `.exe` output requires a Windows-compatible cross-build and a real Windows 7 test.\n",
        encoding="utf-8",
    )


def write_launchers(stage: Path, component: str) -> None:
    bin_dir = stage / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    if component == "zlang":
        posix = "#!/usr/bin/env bash\nset -Eeuo pipefail\nROOT=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\"\nexec python3 \"$ROOT/Zlang/tools/zlangc.py\" \"$@\"\n"
        windows = "@echo off\r\nsetlocal\r\nset ROOT=%~dp0..\r\nwhere py >nul 2>nul && (py -3 \"%ROOT%\\Zlang\\tools\\zlangc.py\" %* & exit /b %errorlevel%)\r\npython \"%ROOT%\\Zlang\\tools\\zlangc.py\" %*\r\n"
        (bin_dir / "zlangc").write_text(posix, encoding="utf-8")
        (bin_dir / "zlangc.cmd").write_text(windows, encoding="utf-8")
    elif component == "zdos":
        posix = "#!/usr/bin/env bash\nset -Eeuo pipefail\nROOT=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\"\nexec python3 \"$ROOT/ZDOS/tools/zdosctl.py\" \"$@\"\n"
        windows = "@echo off\r\nsetlocal\r\nset ROOT=%~dp0..\r\nwhere py >nul 2>nul && (py -3 \"%ROOT%\\ZDOS\\tools\\zdosctl.py\" %* & exit /b %errorlevel%)\r\npython \"%ROOT%\\ZDOS\\tools\\zdosctl.py\" %*\r\n"
        (bin_dir / "zdosctl").write_text(posix, encoding="utf-8")
        (bin_dir / "zdosctl.cmd").write_text(windows, encoding="utf-8")
    else:
        windows = "@echo off\r\nsetlocal\r\ncd /d \"%~dp0..\\SEC\"\r\nwhere npm >nul 2>nul || (echo Node.js/npm required. & exit /b 1)\r\nnpm install\r\nnpm start\r\n"
        (bin_dir / "zdos-sec-start.cmd").write_text(windows, encoding="utf-8")


def build_bundle(name: str, output: Path) -> dict:
    if name == "unified":
        selected = COMPONENTS
    else:
        selected = {name: COMPONENTS[name]}
    with tempfile.TemporaryDirectory(prefix="zdos-lab-pack-") as temp:
        stage = Path(temp) / f"zdos-lab-{name}"
        for key, source in selected.items():
            if not source.is_dir():
                raise FileNotFoundError(source)
            copy_filtered(source, stage / key.upper())
        write_common_files(stage, name)
        for key in selected:
            write_launchers(stage, key)
        manifest = {
            "schema": "zdos-portable-artifact/v1",
            "package": f"zdos-lab-{name}",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "contains_iso": False,
            "components": list(selected),
            "platforms": {
                "linux_x86_64": {"status": "VERIFIED", "format": ["tar.gz", "zip"]},
                "ubuntu_kali_parrot": {"status": "PREPARED", "format": ["tar.gz", "zip"]},
                "windows_7": {"status": "PREPARED", "format": ["zip", "cmd-wrapper"]},
                "native_exe": {"status": "NOT_VERIFIED", "reason": "cross-build and Windows test not available on this host"},
            },
            "source_commits": {},
        }
        for key, source in selected.items():
            try:
                import subprocess
                manifest["source_commits"][key] = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
            except Exception:
                manifest["source_commits"][key] = "unknown"
        (stage / "ARTIFACT-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix == ".zip":
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                for file in sorted(stage.rglob("*")):
                    if file.is_file():
                        archive.write(file, file.relative_to(stage.parent))
        else:
            with tarfile.open(output, "w:gz") as archive:
                archive.add(stage, arcname=stage.name)
    return {"file": str(output), "sha256": sha256(output), "package": f"zdos-lab-{name}", "contains_iso": False}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build non-ISO portable ZDOS Lab bundles")
    parser.add_argument("--component", choices=["zdos", "zlang", "sec", "unified"], default="unified")
    parser.add_argument("--output-dir", default=str(ROOT / "artifacts" / "portable"))
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    artifacts = [
        build_bundle(args.component, output_dir / f"zdos-lab-{args.component}.tar.gz"),
        build_bundle(args.component, output_dir / f"zdos-lab-{args.component}.zip"),
    ]
    sums = output_dir / f"SHA256SUMS-{args.component}"
    sums.write_text("".join(f"{item['sha256']}  {Path(item['file']).name}\n" for item in artifacts), encoding="utf-8")
    aggregate = output_dir / "SHA256SUMS"
    all_artifacts = sorted(output_dir.glob("zdos-lab-*.tar.gz")) + sorted(output_dir.glob("zdos-lab-*.zip"))
    aggregate.write_text("".join(f"{sha256(path)}  {path.name}\n" for path in all_artifacts), encoding="utf-8")
    print(json.dumps({"artifacts": artifacts, "sha256sums": str(sums), "aggregate_sha256sums": str(aggregate)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
