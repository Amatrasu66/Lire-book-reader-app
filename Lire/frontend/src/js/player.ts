/**
 * Lire Dynamic Audio Player
 * Real playback + dynamic uploaded book support
 */

console.log("LIRE PLAYER INITIALIZED");

// =========================
// LOAD SAVED BOOK DATA
// =========================

const savedData =
    localStorage.getItem("currentBook");

const bookData =
    savedData ? JSON.parse(savedData) : null;

// =========================
// PLAYER INIT
// =========================

export function initPlayer() {

    // =========================
    // DOM ELEMENTS
    // =========================

    const playBtn =
        document.getElementById("play-pause");

    const playIcon =
        document.getElementById("play-icon");

    const rewindBtn =
        document.getElementById("rewind");

    const forwardBtn =
        document.getElementById("forward");

    const progressFill =
        document.getElementById("progress-fill");

    const progressContainer =
        document.getElementById("progress-container");

    const currentTimeEl =
        document.getElementById("current-time");

    const durationEl =
        document.getElementById("duration");

    const waveform =
        document.getElementById("waveform");

    const title =
        document.getElementById("playing-title");

    const meta =
        document.getElementById("playing-meta");

    const transcript =
        document.querySelector(".transcription");

    const cover =
        document.getElementById("cover-image");

    // =========================
    // LOAD AUDIO
    // =========================

    const audio = new Audio(
        bookData?.audioUrl || "/audio/test.mp3"
    );

    audio.preload = "metadata";

    // =========================
    // LOAD DYNAMIC CONTENT
    // =========================

    if (bookData) {

        if (title) {

            title.textContent =
                bookData.title || "Untitled Document";
        }

        if (meta) {

            meta.textContent =
                `${bookData.filename} • AI narration ready`;
        }

        if (transcript) {

            const cleanText =
                bookData.text ||
                "No transcript available.";

            transcript.textContent =
                cleanText.slice(0, 800) + "...";
        }

        if (cover instanceof HTMLImageElement && bookData.coverImage) {

            cover.src = bookData.coverImage;
        }
    }

    // =========================
    // PLAYER STATE
    // =========================

    let isPlaying = false;

    // =========================
    // GENERATE WAVEFORM
    // =========================

    if (waveform) {

        waveform.innerHTML = "";

        for (let i = 0; i < 70; i++) {

            const bar =
                document.createElement("div");

            bar.className = "wave-bar";

            const randomHeight =
                12 + Math.random() * 45;

            bar.style.height =
                `${randomHeight}px`;

            waveform.appendChild(bar);
        }
    }

    // =========================
    // PLAY / PAUSE
    // =========================

    playBtn?.addEventListener(
        "click",
        async () => {

            if (isPlaying) {

                audio.pause();

                isPlaying = false;

                if (playIcon) {

                    playIcon.className =
                        "lucide-play";
                }

            } else {

                try {

                    await audio.play();

                    isPlaying = true;

                    if (playIcon) {

                        playIcon.className =
                            "lucide-pause";
                    }

                } catch (err) {

                    console.error(
                        "Audio playback failed:",
                        err
                    );
                }
            }
        });

    // =========================
    // REWIND
    // =========================

    rewindBtn?.addEventListener(
        "click",
        () => {

            audio.currentTime =
                Math.max(0, audio.currentTime - 10);
        });

    // =========================
    // FORWARD
    // =========================

    forwardBtn?.addEventListener(
        "click",
        () => {

            audio.currentTime =
                Math.min(
                    audio.duration,
                    audio.currentTime + 10
                );
        });

    // =========================
    // AUDIO METADATA
    // =========================

    audio.addEventListener(
        "loadedmetadata",
        () => {

            updateDuration();
        });

    // =========================
    // AUDIO TIME UPDATE
    // =========================

    audio.addEventListener(
        "timeupdate",
        () => {

            updateProgress();

            updateWaveform();
        });

    // =========================
    // AUDIO ENDED
    // =========================

    audio.addEventListener(
        "ended",
        () => {

            isPlaying = false;

            if (playIcon) {

                playIcon.className =
                    "lucide-play";
            }
        });

    // =========================
    // SEEK
    // =========================

    progressContainer?.addEventListener(
        "click",
        (e) => {

            const rect =
                progressContainer.getBoundingClientRect();

            const clickX =
                e.clientX - rect.left;

            const width =
                rect.width;

            const percent =
                clickX / width;

            audio.currentTime =
                percent * audio.duration;
        });

    // =========================
    // UPDATE PROGRESS
    // =========================

    function updateProgress() {

        if (!progressFill) return;

        const progress =
            (audio.currentTime / audio.duration) * 100;

        progressFill.style.width =
            `${progress}%`;

        // CURRENT TIME
        if (currentTimeEl) {

            const mins =
                Math.floor(audio.currentTime / 60);

            const secs =
                Math.floor(audio.currentTime % 60);

            currentTimeEl.textContent =
                `${mins
                    .toString()
                    .padStart(2, "0")}:${secs
                        .toString()
                        .padStart(2, "0")}`;
        }
    }

    // =========================
    // UPDATE DURATION
    // =========================

    function updateDuration() {

        if (!durationEl) return;

        const mins =
            Math.floor(audio.duration / 60);

        const secs =
            Math.floor(audio.duration % 60);

        durationEl.textContent =
            `${mins
                .toString()
                .padStart(2, "0")}:${secs
                    .toString()
                    .padStart(2, "0")}`;
    }

    // =========================
    // UPDATE WAVEFORM
    // =========================

    function updateWaveform() {

        const bars =
            document.querySelectorAll(".wave-bar");

        const progress =
            audio.currentTime / audio.duration;

        const activeCount =
            Math.floor(progress * bars.length);

        bars.forEach((bar, index) => {

            const element =
                bar as HTMLElement;

            if (index <= activeCount) {

                element.classList.add("active");

                if (isPlaying) {

                    element.style.height =
                        `${14 + Math.random() * 50}px`;
                }

            } else {

                element.classList.remove("active");

                element.style.height =
                    `${12 + Math.random() * 30}px`;
            }
        });
    }

    // =========================
    // KEYBOARD SHORTCUTS
    // =========================

    document.addEventListener(
        "keydown",
        (e) => {

            // SPACEBAR
            if (e.code === "Space") {

                e.preventDefault();

                playBtn?.dispatchEvent(
                    new Event("click")
                );
            }

            // LEFT ARROW
            if (e.code === "ArrowLeft") {

                audio.currentTime =
                    Math.max(
                        0,
                        audio.currentTime - 5
                    );
            }

            // RIGHT ARROW
            if (e.code === "ArrowRight") {

                audio.currentTime =
                    Math.min(
                        audio.duration,
                        audio.currentTime + 5
                    );
            }
        });
}

// =========================
// START PLAYER
// =========================

initPlayer();