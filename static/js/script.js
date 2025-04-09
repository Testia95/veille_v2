document.addEventListener("DOMContentLoaded", () => {
    const viewed = JSON.parse(localStorage.getItem("viewed_videos") || "[]");

    document.querySelectorAll(".video-card").forEach(card => {
        const id = card.dataset.videoId;
        if (viewed.includes(id)) {
            card.classList.add("vu");
        }

        card.addEventListener("click", () => {
            if (!viewed.includes(id)) {
                viewed.push(id);
                localStorage.setItem("viewed_videos", JSON.stringify(viewed));
                card.classList.add("vu");
            }
        });
    });
});
