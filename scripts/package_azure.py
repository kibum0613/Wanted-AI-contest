"""Package committed source and Linux CPython 3.12 wheels for Azure App Service."""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git", default="git", help="Git executable (git.exe for WSL on a Windows checkout)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    source = subprocess.check_output(
        [args.git, "archive", "--format=tar", "HEAD", "backend", "frontend", "requirements.txt"],
        cwd=root,
    )
    startup = subprocess.check_output(
        [args.git, "show", "HEAD:scripts/start_azure.sh"], cwd=root,
    )
    with tempfile.TemporaryDirectory(prefix="wanted-azure-package-") as temporary:
        work = Path(temporary)
        requirements = work / "requirements.txt"
        with tarfile.open(fileobj=io.BytesIO(source)) as archive:
            member = archive.extractfile("requirements.txt")
            if member is None:
                raise RuntimeError("Committed requirements.txt is missing")
            requirements.write_bytes(member.read())
        packages = work / "site-packages"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
             "--no-compile", "--target", str(packages),
             "--platform", "manylinux2014_x86_64", "--python-version", "3.12",
             "--implementation", "cp", "--abi", "cp312", "--only-binary=:all:",
             "-r", str(requirements)],
            check=True,
        )
        payload = work / "app.tar.gz"
        with tarfile.open(payload, "w:gz") as bundle:
            with tarfile.open(fileobj=io.BytesIO(source)) as archive:
                for member in archive.getmembers():
                    bundle.addfile(member, archive.extractfile(member) if member.isfile() else None)
            bundle.add(packages, arcname=".python_packages/lib/site-packages")
        with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as package:
            package.write(payload, "app.tar.gz")
            package.writestr("start_azure.sh", startup)
    print(f"Created {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
