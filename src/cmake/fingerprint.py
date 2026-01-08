import hashlib
import json
from pathlib import Path

import console

FINGERPRINT_FILE = Path("fingerprint.json")

class Fingerprint:
    def __init__(self, fingerprint_directory : Path):
        self.fingerprint_directory_ = fingerprint_directory
        self.fingerprint_file_ = fingerprint_directory / FINGERPRINT_FILE

    def load_or_create(self) : 
        # Create file if not exist
        if self.fingerprint_file_.exists():
            with self.fingerprint_file_.open("r", encoding="utf-8") as f:
                try:
                    self.json_ = json.load(f)
                except json.JSONDecodeError as e:
                    console.print_error(f"Error when loading {self.fingerprint_file_}. Ignore it.\n{e}")
                    self.json_ = {}
        else: 
            self.fingerprint_directory_.mkdir(parents=True, exist_ok=True)
            self.fingerprint_file_.write_text("{}", encoding="utf-8")
            self.json_ = {}

    def save(self):
        with self.fingerprint_file_.open("w", encoding="utf-8") as f:
            json.dump(self.json_, f, indent=2)
    
    @staticmethod
    def compute_file_hash(file_to_hash : Path) -> str:
        h = hashlib.new("sha256")
        file_to_hash = file_to_hash.resolve()
        if not file_to_hash.exists():
            raise FileNotFoundError(file_to_hash)
        with file_to_hash.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        digest = h.hexdigest()
        return digest

    def is_fresh_file(self, filename: Path) -> bool:
        filename = filename.resolve()
        if not filename.exists():
            return False
        key = str(filename)

        if key not in self.json_:
            return False

        entry = self.json_[key]

        # récupération des métadonnées stockées
        stored_size = entry.get("size")
        stored_mtime = entry.get("mtime_ns")

        # récupération des métadonnées actuelles
        stat = filename.stat()
        current_size = stat.st_size
        current_mtime = stat.st_mtime_ns

        # Si size ou mtime diffèrent → fichier modifié
        if stored_size != current_size or stored_mtime != current_mtime:
            return False

        # Sinon, vérification du hash (inutile dans la plupart des cas)
        current_hash = self.compute_file_hash(filename)
        stored_hash = entry.get("hash")
        return stored_hash == current_hash
    
    def update_file(self, filename: Path):
        filename = filename.resolve()
        key = str(filename)
        file_hash = self.compute_file_hash(filename)
        stat = filename.stat()
        self.json_[key] = {
                "file": key,
                "hash": file_hash,
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
        }