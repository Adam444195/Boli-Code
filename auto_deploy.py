import os
import re
import subprocess

FILE_PATH = "Boli_code_python_terminal.py"
EXE_NAME = "Boli.Code.exe"

def run_cmd(cmd):
    """Exécute une commande shell et affiche son statut."""
    print(f"\n➔ Exécution : {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de : {cmd}")
        return False
    return True

# ---------------------------------------------------------------------------
# 1. Incrémentation automatique de la version dans le fichier source .py
# ---------------------------------------------------------------------------
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

new_version_str = ""

def inc_version(match):
    global new_version_str
    version_num = int(match.group(1)) + 1
    new_version_str = f"v.{version_num:04d}"
    return f'CURRENT_VERSION = "{new_version_str}"'

# Remplace v.0002 par v.0003, v.0004, etc.
new_content = re.sub(r'CURRENT_VERSION\s*=\s*"v\.(\d+)"', inc_version, content)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"📌 Version incrémentée avec succès : {new_version_str}")

# ---------------------------------------------------------------------------
# 2. Recompilation en .exe avec PyInstaller
# ---------------------------------------------------------------------------
if not run_cmd(f"pyinstaller --onefile --name=Boli.Code {FILE_PATH}"):
    print("❌ Échec de la compilation PyInstaller.")
    exit(1)

# ---------------------------------------------------------------------------
# 3. Synchronisation Git (Commit + Push)
# ---------------------------------------------------------------------------
commit_msg = f"Mise à jour automatique {new_version_str}"
run_cmd("git add .")
run_cmd(f'git commit -m "{commit_msg}"')
run_cmd("git push origin main")

# ---------------------------------------------------------------------------
# 4. Publication de la Release GitHub avec le nouvel .exe
# ---------------------------------------------------------------------------
exe_path = os.path.join("dist", EXE_NAME)

if os.path.exists(exe_path):
    cmd_release = f'gh release create {new_version_str} "{exe_path}#Boli.Code.exe" --title "{new_version_str}" --notes "Mise à jour automatique {new_version_str}"'
    if run_cmd(cmd_release):
        print(f"\n🚀 [SUCCÈS] {EXE_NAME} version {new_version_str} a été compilé, pushé et publié sur GitHub !")
else:
    print(f"❌ Erreur : L'exécutable {exe_path} est introuvable.")