import subprocess
from pathlib import Path

# Base du projet
project_root = Path(__file__).parent

# Dossier de shadow build
build_dir = project_root / "build"
dist_dir = build_dir / "exe"   # exe final
work_dir = build_dir / "tmp"   # fichiers temporaires PyInstaller
spec_dir = build_dir / "spec"  # spec PyInstaller

# Création des dossiers
for d in [dist_dir, work_dir, spec_dir]:
    d.mkdir(parents=True, exist_ok=True)

# Commande PyInstaller
pyinstaller_cmd = [
    "pyinstaller",
    "--name", "kiss",
    "--onefile",
    "--optimize=2",
    f"--distpath={dist_dir}",
    f"--workpath={work_dir}",
    f"--specpath={spec_dir}",
    "src/kiss/kiss.py"
]

subprocess.run(pyinstaller_cmd)
