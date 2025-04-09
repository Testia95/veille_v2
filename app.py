from flask import Flask, render_template, abort
import feedparser, os, json
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Chargement des flux RSS des médias
with open("data/medias.json", "r", encoding="utf-8") as f:
    flux_dict = json.load(f)

# Chargement des descriptions des médias (pour la page média)
with open("data/descriptions.json", "r", encoding="utf-8") as f:
    descriptions = json.load(f)

# Catégories politiques définies
categories = ["Gauche", "Droite", "Centre", "Autre"]

# 🔍 Récupère l'ID de la vidéo depuis l'URL YouTube
def get_video_id(url):
    return url.split("v=")[-1]

# 📡 Fonction principale pour parser un flux et retourner les vidéos récentes
def get_recent_videos(url, jours_max=14):
    flux = feedparser.parse(url)
    now = datetime.now()
    limite = timedelta(days=jours_max)
    videos = []

    for entry in flux.entries:
        try:
            published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except:
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
                "id": video_id,
                "is_short": "#shorts" in entry.title.lower()  # 📱 Détection d’un short
            })
    return videos

# 🏠 Route d’accueil par défaut (redirige vers /videos pour cohérence)
@app.route("/")
def index():
    return videos()

# 📺 Route : vidéos longues uniquement (par défaut)
@app.route("/videos")
def videos():
    videos_par_orientation = {cat: [] for cat in categories}
    videos_recents = []
    sidebar_videos = {}

    for media, data in flux_dict.items():
        flux_url = data["flux"]
        orientation = data.get("orientation", "Autre")
        videos = get_recent_videos(flux_url, jours_max=14)

        # 🔍 On ne garde que les vidéos classiques
        videos_filtrees = [v for v in videos if not v["is_short"]]
        videos_with_media = [dict(v, media=media) for v in videos_filtrees]

        videos_par_orientation[orientation].extend(videos_with_media)
        videos_recents.extend(videos_with_media)
        sidebar_videos[media] = videos[:5]  # Toujours les 5 derniers tous types confondus

    for lst in videos_par_orientation.values():
        lst.sort(key=lambda x: x["timestamp"], reverse=True)

    videos_recents.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("videos.html",
        flux_dict=flux_dict,
        videos_par_orientation=videos_par_orientation,
        videos_recents=videos_recents,
        sidebar_videos=sidebar_videos)

# 🎞️ Route : shorts uniquement
@app.route("/shorts")
def shorts():
    videos_par_orientation = {cat: [] for cat in categories}
    videos_recents = []
    sidebar_videos = {}

    for media, data in flux_dict.items():
        flux_url = data["flux"]
        orientation = data.get("orientation", "Autre")
        videos = get_recent_videos(flux_url, jours_max=14)

        # 🔍 On ne garde que les shorts
        shorts_filtres = [v for v in videos if v["is_short"]]
        shorts_with_media = [dict(v, media=media) for v in shorts_filtres]

        videos_par_orientation[orientation].extend(shorts_with_media)
        videos_recents.extend(shorts_with_media)
        sidebar_videos[media] = videos[:5]

    for lst in videos_par_orientation.values():
        lst.sort(key=lambda x: x["timestamp"], reverse=True)

    videos_recents.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("shorts.html",
        flux_dict=flux_dict,
        videos_par_orientation=videos_par_orientation,
        videos_recents=videos_recents,
        sidebar_videos=sidebar_videos)

# 🗂️ Route : page dédiée à un média
@app.route("/media/<nom>")
def page_media(nom):
    if nom not in flux_dict:
        abort(404)

    flux_url = flux_dict[nom]["flux"]
    videos = get_recent_videos(flux_url, jours_max=60)
    sidebar_videos = {m: get_recent_videos(data["flux"], jours_max=14)[:5] for m, data in flux_dict.items()}
    description = descriptions.get(nom, "Aucune description disponible.")

    return render_template("media.html",
        media=nom,
        description=description,
        videos=videos,
        flux_dict=flux_dict,
        sidebar_videos=sidebar_videos)

# 📚 Route : pages statiques
@app.route("/decryptage")
def decryptage():
    return render_template("decryptage.html")

@app.route("/manifeste")
def manifeste():
    return render_template("manifeste.html")

# 🧪 Pour lancer en local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
