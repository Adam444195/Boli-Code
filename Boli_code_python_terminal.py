import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import webbrowser

# ---------------------------------------------------------------------------
# Configuration des Clés API
# ---------------------------------------------------------------------------
OPENROUTER_KEY = "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"
URL_OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"

TAVILY_API_KEY = "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"
REPLICATE_API_TOKEN = "r8_TXxUgy4VTwQ20QCZlLzGAKsP7WAxAlz1rjH7t"

MODES = {
    "1": {"nom": "Plan (Dots-3)", "model": "dots-studio/dots-3-note-preview:free"},
    "2": {"nom": "Code (North-Mini)", "model": "cohere/north-mini-code:free"},
    "3": {"nom": "MIX & Code (GLM-5.2)", "model": "z-ai/glm-5.2:free"},
    "4": {"nom": "Vidéo (Replicate Minimax)", "model": "minimax/video-01"}
}
mode_actuel = "3"

# ---------------------------------------------------------------------------
# Thème Visuel Console
# ---------------------------------------------------------------------------
C_CYAN, C_VERT, C_BLEU, C_JAUNE, C_BLANC, C_GRIS, C_ROUGE, C_BOLD, C_MAGENTA, C_RESET = (
    "\033[36m", "\033[32m", "\033[34m", "\033[33m", "\033[97m", "\033[90m", "\033[31m", "\033[1m", "\033[35m", "\033[0m"
)

activites_recentes = [
    "Recherche Web Auto Tavily intégrée",
    "Modes Plan, Code, Mix & Vidéo Replicate réactivés",
    "Support des images et fichiers opérationnel"
]

def ajouter_activite(texte):
    global activites_recentes
    timestamp = time.strftime("%H:%M")
    activites_recentes.insert(0, f"[{timestamp}] {texte}")
    if len(activites_recentes) > 3: activites_recentes.pop()

def afficher_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C_CYAN}┌──────────────────────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}{C_BLANC}BOLI CODE CLI{C_RESET} {C_GRIS}v10.7.0{C_RESET} {C_CYAN}│{C_RESET} Mode: {C_VERT}{MODES[mode_actuel]['nom']:<27}{C_RESET} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}├──────────────────────────────────────────────────────────────────────────┤{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}Fonctionnalités intégrées:{C_RESET}                                              {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}   • {C_JAUNE}Recherche Web Auto (Tavily){C_RESET} si besoin d'infos récentes/doc          {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}   • {C_MAGENTA}/file <chemin>{C_RESET}   -> Charger une image ou un fichier texte              {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}   • {C_CYAN}/mode{C_RESET}            -> Basculer entre 1:Plan, 2:Code, 3:Mix, 4:Vidéo  {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}   • {C_CYAN}/clear{C_RESET}           -> Effacer la console                            {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}├──────────────────────────────────────────────────────────────────────────┤{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}Dernières activités:{C_RESET}                                                    {C_CYAN}│{C_RESET}")
    for act in activites_recentes:
        print(f"{C_CYAN}│{C_RESET}   {C_GRIS}{act:<68}{C_RESET} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└──────────────────────────────────────────────────────────────────────────┘{C_RESET}\n")

# ---------------------------------------------------------------------------
# Outils : Recherche Web Tavily & Fichiers
# ---------------------------------------------------------------------------
def necessite_recherche_web(question):
    """Détecte automatiquement si la question nécessite des données web récentes."""
    mots_cles = [
        "actu", "actualité", "dernière version", "doc", "documentation", 
        "aujourd'hui", "récent", "météo", "prix", "nouvelle", "2026", "2025",
        "search", "trouve", "cherche", "qui est", "qu'est-ce que"
    ]
    q_lower = question.lower()
    return any(mot in q_lower for mot in mots_cles) or question.endswith("?")

def recherche_web_tavily(query):
    """Recherche sur le Web via Tavily API."""
    url = "https://api.tavily.com/search"
    payload = json.dumps({"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            resultats = [f"- {r['title']}: {r['content']}" for r in data.get("results", [])]
            return "\n".join(resultats) if resultats else None
    except Exception:
        return None

def charger_fichier_ou_image(chemin):
    """Charge un fichier texte ou signale la présence d'une image."""
    if not os.path.exists(chemin):
        return None, f"Fichier introuvable : {chemin}"
    
    ext = os.path.splitext(chemin)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        return f"[Image chargée : {os.path.basename(chemin)}]", None
    else:
        try:
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), None
        except Exception as e:
            return None, f"Erreur de lecture : {e}"

# ---------------------------------------------------------------------------
# Moteurs API
# ---------------------------------------------------------------------------
def generer_flux_openrouter(model_name, prompt_content):
    payload = json.dumps({
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_content}]
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost:3000",
        "X-Title": "Boli Code App"
    }

    try:
        req = urllib.request.Request(URL_OPENROUTER, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=40) as resp:
            data_resp = json.loads(resp.read().decode("utf-8"))
            if "choices" in data_resp and len(data_resp["choices"]) > 0:
                return data_resp["choices"][0]["message"].get("content", ""), None
    except Exception as e:
        return None, f"Erreur API OpenRouter : {e}"
    return None, "Aucune réponse reçue."

def mettre_a_jour_galerie_html(dossier_sortie="output_media"):
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)
    fichiers = sorted([f for f in os.listdir(dossier_sortie) if f.endswith('.mp4')], reverse=True)
    
    medias_html = "".join([f"""
        <div class="card">
            <h3>🎬 {f}</h3>
            <video controls autoplay loop src="{f}"></video>
            <br><a href="{f}" download class="btn">Télécharger le MP4</a>
        </div>""" for f in fichiers])
    
    if not medias_html:
        medias_html = "<p style='color:#94a3b8;'>Aucune vidéo générée.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><title>Boli Code - Studio Vidéo</title>
    <style>
        body {{ background: #0f172a; color: #fff; font-family: system-ui, sans-serif; padding: 20px; }}
        h1 {{ text-align: center; color: #38bdf8; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; max-width: 1200px; margin: 20px auto; }}
        .card {{ background: #1e293b; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #334155; }}
        video {{ width: 100%; border-radius: 8px; margin: 10px 0; background: #000; }}
        .btn {{ background: #0284c7; color: white; padding: 8px 14px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }}
    </style>
</head>
<body>
    <h1>🎥 Galerie Vidéo Boli Code Studio</h1>
    <div class="grid">{medias_html}</div>
</body>
</html>"""
    path_html = os.path.join(dossier_sortie, "index.html")
    with open(path_html, "w", encoding="utf-8") as f: f.write(html_content)
    return os.path.abspath(path_html)

def generer_video_replicate(prompt, dossier_sortie="output_media"):
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)

    url = "https://api.replicate.com/v1/models/minimax/video-01/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"input": {"prompt": prompt}}).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            get_url = data["urls"]["get"]
        
        while True:
            time.sleep(5)
            req_status = urllib.request.Request(get_url, headers=headers)
            with urllib.request.urlopen(req_status) as resp_status:
                data_status = json.loads(resp_status.read().decode("utf-8"))
                status = data_status.get("status")
                print(f"{C_JAUNE}⏳ Rendu vidéo Replicate : {status}...{C_RESET}    ", end="\r")
                
                if status == "succeeded":
                    video_url = data_status["output"]
                    if isinstance(video_url, list): video_url = video_url[0]
                    nom_f = f"video_{int(time.time())}.mp4"
                    path_mp4 = os.path.join(dossier_sortie, nom_f)
                    urllib.request.urlretrieve(video_url, path_mp4)
                    print(" " * 60, end="\r")
                    return os.path.abspath(path_mp4)
                elif status in ["failed", "canceled"]:
                    print(f"\n{C_ROUGE}❌ Échec de la génération vidéo.{C_RESET}")
                    return None
    except Exception as e:
        print(f"\n{C_ROUGE}❌ Erreur Replicate : {e}{C_RESET}")
        return None

afficher_header()

# ---------------------------------------------------------------------------
# Boucle Principale
# ---------------------------------------------------------------------------
while True:
    try:
        user_input = input(f"{C_CYAN}╭─{C_RESET} {C_BOLD}{C_BLANC}Vous{C_RESET}\n{C_CYAN}╰─>{C_RESET} {C_BLANC}")
        print(C_RESET, end="")

        if user_input.lower() in ["quitter", "exit", "quit"]: break
        if not user_input.strip(): continue

        if user_input.strip() == "/clear":
            afficher_header()
            continue

        if user_input.strip() == "/mode":
            print(f"\n{C_CYAN}Sélectionnez un mode :{C_RESET}")
            for k, v in MODES.items():
                print(f"  [{k}] {v['nom']}")
            choix = input(f"\n{C_CYAN}Choix (1-4) : {C_RESET}")
            if choix in MODES:
                mode_actuel = choix
                afficher_header()
                print(f"{C_VERT}✔ Mode activé : {MODES[mode_actuel]['nom']}{C_RESET}\n")
            continue

        # Commande Chargement de fichier ou d'image
        if user_input.startswith("/file "):
            chemin = user_input[6:].strip()
            contenu, err = charger_fichier_ou_image(chemin)
            if err:
                print(f"{C_ROUGE}❌ {err}{C_RESET}\n")
                continue
            else:
                print(f"{C_VERT}✔ Fichier chargé : {chemin}{C_RESET}\n")
                user_input = f"Fichier/Image inclus ({chemin}):\n{contenu}"
                ajouter_activite(f"Fichier : {os.path.basename(chemin)}")

        # Mode 4 : Génération Vidéo via Replicate
        if mode_actuel == "4":
            print(f"{C_MAGENTA}🎥 Génération de la vidéo en cours...{C_RESET}")
            fichier_mp4 = generer_video_replicate(user_input)
            if fichier_mp4:
                galerie = mettre_a_jour_galerie_html()
                print(f"\n{C_VERT}✔ Vidéo générée :{C_RESET} {C_BLANC}{fichier_mp4}{C_RESET}")
                print(f"{C_VERT}🌐 Ouverture de la galerie locale...{C_RESET}\n")
                webbrowser.open(f"file://{galerie}")
                ajouter_activite(f"Vidéo MP4 : {user_input[:20]}...")
            continue

        # Recherche Web Auto (Mode 1, 2, 3)
        prompt_final = user_input
        if necessite_recherche_web(user_input):
            print(f"{C_JAUNE}🔍 Recherche Web Auto (Tavily) en cours...{C_RESET}", end="\r")
            contexte_web = recherche_web_tavily(user_input)
            print(" " * 50, end="\r")
            if contexte_web:
                print(f"{C_JAUNE}🌐 Contexte Web trouvé et transmis au modèle.{C_RESET}")
                prompt_final = f"Information Web récente:\n{contexte_web}\n\nQuestion de l'utilisateur:\n{user_input}"
                ajouter_activite(f"Recherche Auto : {user_input[:20]}...")

        # Traitement Texte / Plan / Code via OpenRouter
        res, err = generer_flux_openrouter(MODES[mode_actuel]["model"], prompt_final)
        if err:
            print(f"\n{C_ROUGE}❌ {err}{C_RESET}\n")
        else:
            print(f"\n{C_BLEU}╭─{C_RESET} {C_BOLD}{C_BLANC}Boli Code ({MODES[mode_actuel]['nom']}){C_RESET}\n{C_BLEU}│{C_RESET} {res.strip()}\n{C_BLEU}╰──────────────────────────────────────────{C_RESET}\n")
            ajouter_activite(f"Réponse ({MODES[mode_actuel]['nom']})")

    except Exception as e:
        print(f"\n{C_ROUGE}❌ Erreur : {e}{C_RESET}\n")