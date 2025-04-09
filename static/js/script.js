// Fonction d'initialisation
document.addEventListener("DOMContentLoaded", () => {
    const viewed = JSON.parse(localStorage.getItem("viewed_videos") || "[]");

    // Applique la classe "vu" aux vidéos déjà vues
    document.querySelectorAll(".video-card").forEach(card => {
        const id = card.dataset.videoId;
        if (viewed.includes(id)) {
            card.classList.add("vu");
        }

        // Quand on clique sur une vidéo → on la marque comme vue
        card.addEventListener("click", () => {
            if (!viewed.includes(id)) {
                viewed.push(id);
                localStorage.setItem("viewed_videos", JSON.stringify(viewed));
                card.classList.add("vu");
            }
        });
    });
});
