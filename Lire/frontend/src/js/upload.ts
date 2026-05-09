/**
 * Lire Upload System
 * Real backend integration
 */

export function initUpload() {

    const dropZone = document.getElementById('drop-zone');

    const fileInput =
        document.getElementById('file-input') as HTMLInputElement;

    const startBtn =
        document.getElementById('start-btn');

    // UI STATES
    const idleState =
        document.getElementById('upload-idle');

    const loadingState =
        document.getElementById('upload-loading');

    const successState =
        document.getElementById('upload-success');

    const progressBar =
        document.getElementById('progress-bar');

    const filenameDisplay =
        document.getElementById('ready-filename');

    const toast =
        document.getElementById('toast');

    if (!dropZone) return;

    // =========================
    // DRAG EVENTS
    // =========================

    ['dragenter', 'dragover', 'dragleave', 'drop']
        .forEach(eventName => {

            dropZone.addEventListener(
                eventName,
                preventDefaults,
                false
            );
        });

    function preventDefaults(e: Event) {

        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover']
        .forEach(eventName => {

            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragging');
            });
        });

    ['dragleave', 'drop']
        .forEach(eventName => {

            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragging');
            });
        });

    // =========================
    // DROP
    // =========================

    dropZone.addEventListener('drop', (e: DragEvent) => {

        const files = e.dataTransfer?.files;

        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    });

    // =========================
    // CLICK
    // =========================

    startBtn?.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {

        if (fileInput.files?.[0]) {
            handleFile(fileInput.files[0]);
        }
    });

    // =========================
    // MAIN HANDLER
    // =========================

    async function handleFile(file: File) {

        const validTypes = [
            'application/pdf',
            'text/plain',
            'application/epub+zip'
        ];

        if (
            !validTypes.includes(file.type)
            &&
            !file.name.endsWith('.epub')
        ) {

            showToast(
                'Only PDF, TXT, and EPUB are supported'
            );

            return;
        }

        // UI LOADING
        idleState!.style.display = 'none';
        loadingState!.style.display = 'block';

        animateFakeProgress();

        try {

            const formData = new FormData();

            formData.append('file', file);

            // =========================
            // BACKEND REQUEST
            // =========================

            const response = await fetch(
                'http://127.0.0.1:5000/upload',
                {
                    method: 'POST',
                    body: formData
                }
            );

            const data = await response.json();

            console.log(data);

            // =========================
            // SAVE FOR PLAYER
            // =========================

            const playerData = {

                title:
                    file.name.replace(/\.[^/.]+$/, ""),

                filename:
                    file.name,

                text:
                    data.text ||
                    "No extracted text available.",

                audioUrl:
                    '/audio/test.mp3',

                coverImage:
                    'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=1200&auto=format&fit=crop'
            };

            localStorage.setItem(
                'currentBook',
                JSON.stringify(playerData)
            );

            // SUCCESS UI
            loadingState!.style.display = 'none';

            successState!.style.display = 'block';

            if (filenameDisplay) {
                filenameDisplay.textContent = file.name;
            }

            showToast('Document processed successfully');

            // AUTO REDIRECT
            setTimeout(() => {

                window.location.href = '/player.html';

            }, 1200);

        } catch (err) {

            console.error(err);

            loadingState!.style.display = 'none';

            idleState!.style.display = 'block';

            showToast('Upload failed');
        }
    }

    // =========================
    // FAKE PROGRESS
    // =========================

    function animateFakeProgress() {

        let progress = 0;

        const interval = setInterval(() => {

            progress += Math.random() * 12;

            if (progress >= 95) {

                progress = 95;

                clearInterval(interval);
            }

            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }

        }, 250);
    }

    // =========================
    // TOAST
    // =========================

    function showToast(msg: string) {

        const toastMsg =
            document.getElementById('toast-msg');

        if (toastMsg) {
            toastMsg.textContent = msg;
        }

        toast?.classList.add('show');

        setTimeout(() => {
            toast?.classList.remove('show');
        }, 3000);
    }
}

initUpload();