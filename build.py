import subprocess
from pathlib import Path

# Root directory
project_root = Path(__file__).parent

# Shadow build
build_dir = project_root / "build"
dist_dir = build_dir / "bin"   # Final binary
work_dir = build_dir / "tmp"   # PyInstaller temp files
spec_dir = build_dir / "spec"  # PyInstaller spec files

# Create directory
for d in [dist_dir, work_dir, spec_dir]:
    d.mkdir(parents=True, exist_ok=True)

# Run PyInstaller
pyinstaller_cmd = [
    "pyinstaller",
    "--name", "kiss",
    "--onefile",
    "--optimize=2",
    f"--distpath={dist_dir}",
    f"--workpath={work_dir}",
    f"--specpath={spec_dir}",
    "src/kiss.py"
]

subprocess.run(pyinstaller_cmd)
