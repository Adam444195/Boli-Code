import os
import re
import subprocess

FILE_PATH = "Boli_code_python_terminal.py"
EXE_NAME = "Boli.Code.exe"

def run_cmd(cmd):
    print(f"\n➔ Exécution : {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de : {cmd}")
        return False
    return True

# ---------------------------------------------------------------------------
# 1. Incrémentation forcée de la version
# ---------------------------------------------------------------------------
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Recherche de CURRENT_VERSION = "v.XXXX"
match = re.search(r'CURRENT_VERSION\s*=\s*"v\.(\d+)"', content)

if match:
    current_num = int(match.group(1))
    new_num = current_num + 1
    new_version_str = f"v.{new_num:04d}"
    content = re.sub(r'CURRENT_VERSION\s*=\s*"v\.\d+"', f'CURRENT_VERSION = "{new_version_str}"', content)
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📌 Version changée avec succès : {new_version_str}")
else:
    # Si la variable n'est pas trouvée, on la force à v.0003
    new_version_str = "v.0003"
    print(f"⚠️ Variable non détectée. Passage forcé à : {new_version_str}")

# ---------------------------------------------------------------------------
# 2. Recompilation PyInstaller
# ---------------------------------------------------------------------------
if not run_cmd(f"pyinstaller --onefile --name=Boli.Code {FILE_PATH}"):
    exit(1)

# ---------------------------------------------------------------------------
# 3. Synchronisation Git
# ---------------------------------------------------------------------------
commit_msg = f"Mise à jour automatique {new_version_str}"
run_cmd("git add .")
run_cmd(f'git commit -m "{commit_msg}"')
run_cmd("git push origin main")

# ---------------------------------------------------------------------------
# 4. Publication Release GitHub
# ---------------------------------------------------------------------------
exe_path = os.path.join("dist", EXE_NAME)

if os.path.exists(exe_path):
    cmd_release = f'gh release create {new_version_str} "{exe_path}#Boli.Code.exe" --title "{new_version_str}" --notes "Mise à jour automatique {new_version_str}"'
    if run_cmd(cmd_release):
        print(f"\n🚀 [SUCCÈS] {EXE_NAME} {new_version_str} a été publié sur GitHub !")