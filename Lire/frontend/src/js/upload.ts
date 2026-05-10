/**
 * Lire Upload System
 * Fully Dynamic Upload + Persistent Session
 */

export function initUpload() {

    const dropZone =
        document.getElementById('drop-zone');

    const fileInput =
        document.getElementById('file-input') as HTMLInputElement;

    const startBtn =
        document.getElementById('start-btn');

    const idleState =
        document.getElementById('upload-idle');

    const loadingState =
        document.getElementById('upload-loading');

    const successState =
        document.getElementById('upload-success');

    const progressBar =
        document.getElementById('progress-bar');

    if (!dropZone) return;

    startBtn?.addEventListener('click', () => {

        fileInput.click();
    });

    fileInput.addEventListener('change', () => {

        if (fileInput.files?.[0]) {

            handleFile(fileInput.files[0]);
        }
    });

    // =========================
    // DRAG & DROP HANDLERS
    // =========================

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragging');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragging');
        }, false);
    });

    dropZone.addEventListener('drop', (e: DragEvent) => {
        const dt = e.dataTransfer;
        const files = dt?.files;

        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    });

    const API_BASE = (import.meta as any).env.VITE_API_URL || 'http://127.0.0.1:5000';

    async function handleFile(file: File) {

        idleState!.style.display = 'none';

        loadingState!.style.display = 'block';

        animateProgress();

        try {

            const formData = new FormData();

            formData.append('file', file);

            const response = await fetch(
                `${API_BASE}/upload`,
                {
                    method: 'POST',
                    body: formData
                }
            );

            const data = await response.json();

            console.log("UPLOAD RESPONSE:", data);

            if (!data.success) {

                throw new Error(
                    data.error || "Upload failed"
                );
            }

            const playerData = {

                title:
                    data.title,

                text:
                    data.text,

                chunks: data.chunks.map((ch: any) => ({
                    ...ch,
                    audio_url: `${API_BASE}${ch.audio_url}`
                })),

                coverImage:
                    data.cover_image ? `${API_BASE}${data.cover_image}` : null,

                uploadedAt:
                    Date.now()
            };

            localStorage.setItem(
                'currentBook',
                JSON.stringify(playerData)
            );

            loadingState!.style.display = 'none';

            successState!.style.display = 'block';

            setTimeout(() => {

                window.location.href =
                    '/player.html';

            }, 1500);

        } catch (err) {

            console.error(err);

            loadingState!.style.display = 'none';

            idleState!.style.display = 'block';

            alert('Upload failed');
        }
    }

    function animateProgress() {

        let progress = 0;

        const interval = setInterval(() => {

            progress += Math.random() * 10;

            if (progress >= 95) {

                progress = 95;

                clearInterval(interval);
            }

            if (progressBar) {

                progressBar.style.width =
                    `${progress}%`;
            }

        }, 250);
    }
}

initUpload();