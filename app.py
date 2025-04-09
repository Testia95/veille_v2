from flask import Flask, render_template, abort
import feedparser
import os
import json
from datetime import datetime, timedelta
import time

app = Flask(__name__)

with open("data/medias.json", "r", encoding="utf-8") as f:
    flux_dict = json.load(f)

categories = ["Gauche", "Droite", "Centre", "Autre"]

def get_video_id(url):
    return url.split("v=")[-1]

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
                "id": video_id
            })

    return videos

@app.route("/")
def index():
    videos_par_orientation = {cat: [] for cat in categories}
    videos_recents = []
    sidebar_videos = {}

    for media, data in flux_dict.items():
        flux_url = data["flux"]
        orientation = data.get("orientation", "Autre")
        videos = get_recent_videos(flux_url, jours_max=14)

        # Séparation par orientation
        videos_par_orientation[orientation].extend([dict(v, media=media) for v in videos])
        videos_recents.extend([dict(v, media=media) for v in videos])

        # Stockage des 5 dernières pour la sidebar
        sidebar_videos[media] = videos[:5]

    videos_recents.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("home.html",
                           flux_dict=flux_dict,
                           videos_par_orientation=videos_par_orientation,
                           videos_recents=videos_recents,
                           sidebar_videos=sidebar_videos)

@app.route("/media/<nom>")
def page_media(nom):
    if nom not in flux_dict:
        abort(404)

    flux_url = flux_dict[nom]["flux"]
    videos = get_recent_videos(flux_url, jours_max=60)
    sidebar_videos = {m: get_recent_videos(data["flux"], jours_max=14)[:5] for m, data in flux_dict.items()}

    return render_template("media.html", media=nom, videos=videos, flux_dict=flux_dict, sidebar_videos=sidebar_videos)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
