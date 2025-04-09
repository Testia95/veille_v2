from flask import Flask, render_template, abort
import feedparser
import os
import json
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# 🔄 Charge les flux RSS et orientations politiques depuis le fichier JSON
with open("data/medias.json", "r", encoding="utf-8") as f:
    flux_dict = json.load(f)

# 🧠 Prépare les catégories à l’avance
categories = ["Gauche", "Droite", "Centre", "Autre"]

# 🔧 Fonction utilitaire pour extraire l’ID d’une vidéo à partir de l’URL
def get_video_id(url):
    return url.split("v=")[-1]

# 🔧 Fonction pour récupérer les vidéos à partir d’un flux, avec limite de temps
def get_recent_videos(url, jours_max=14):
    flux = feedparser.parse(url)
    now = datetime.now()
    limite = timedelta(days=jours_max)
    videos = []

    for entry in flux.entries:
        try:
            published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except Exception:
            continue

        if now - published <= limite:
            video_id = get_video_id(entry.link)
            videos.append({
                "titre": entry.title,
                "lien": entry.link,
                "date": published.strftime("%d %B %Y à %Hh%M"),
                "timestamp": published.timestamp(),
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "embed": f"https://www.youtube.com/embed/{video_id}",
                "id": video_id
            })

    return videos

# 🌍 Route principale : page d’accueil
@app.route("/")
def index():
    videos_par_orientation = {cat: [] for cat in categories}
    videos_recents = []

    for media, data in flux_dict.items():
        flux_url = data["flux"]
        orientation = data.get("orientation", "Autre")
        videos = get_recent_videos(flux_url, jours_max=14)

        # Ajoute au groupe idéologique
        videos_par_orientation[orientation].extend([
            dict(v, media=media) for v in videos
        ])

        # Ajoute aux dernières vidéos toutes chaînes confondues
        videos_recents.extend([
            dict(v, media=media) for v in videos
        ])

    # Trie les vidéos globales par date de publication
    videos_recents.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("home.html",
                           flux_dict=flux_dict,
                           videos_par_orientation=videos_par_orientation,
                           videos_recents=videos_recents)

# 🌍 Page individuelle pour chaque média
@app.route("/media/<nom>")
def page_media(nom):
    if nom not in flux_dict:
        abort(404)

    flux_url = flux_dict[nom]["flux"]
    videos = get_recent_videos(flux_url, jours_max=60)

    return render_template("media.html", media=nom, videos=videos)

# 🚀 Démarrage du serveur
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)