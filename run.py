import sys
import os
import subprocess

# Détecte le système et choisit l'exécutable correct
bin = "build/bin/kiss.exe" if os.name == "nt" else "build/bin/kiss"

# Arguments passés au script
args = [bin] + sys.argv[1:]

# Exécute le binaire
subprocess.run(args)