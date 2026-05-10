/**
 * Lire Dynamic Player
 */

export function initPlayer() {

    const saved =
        localStorage.getItem('currentBook');

    if (!saved) {

        window.location.href =
            '/index.html';

        return;
    }

    const data = JSON.parse(saved);

    console.log("PLAYER DATA:", data);

    const titleEl =
        document.getElementById('playing-title');

    const metaEl =
        document.getElementById('playing-meta');

    const coverEl =
        document.getElementById('cover-image') as HTMLImageElement;

    const transcriptEl =
        document.getElementById('transcript-content');

    const waveform =
        document.getElementById('waveform');

    const progressFill =
        document.getElementById('progress-fill');

    const progressContainer =
        document.getElementById('progress-container');

    const currentTimeEl =
        document.getElementById('current-time');

    const durationEl =
        document.getElementById('duration');

    const playBtn =
        document.getElementById('play-pause');

    const playIcon =
        document.getElementById('play-icon');

    // =========================
    // DYNAMIC CONTENT - PARAGRAPH SPLIT
    // =========================

    titleEl!.textContent = data.title;
    metaEl!.textContent = 'AI narration ready';

    if (data.coverImage) {
        coverEl.src = data.coverImage;
    }

    // Split smartly into meaningful chunks (paragraphs or grouped sentences)
    let rawSegments = data.text.split(/\n\s*\n/).filter((s: string) => s.trim().length > 0);
    
    // Fallback logic if text lacks paragraph breaks: group every 3 sentences
    if (rawSegments.length < 4) {
        const allSentences = data.text.split(/(?<=[.!?])\s+/).filter((s: string) => s.trim().length > 0);
        const grouped = [];
        for (let i = 0; i < allSentences.length; i += 3) {
            grouped.push(allSentences.slice(i, i + 3).join(' '));
        }
        rawSegments = grouped;
    }

    // =========================
    // PROPORTIONAL TIMING ENGINE
    // =========================
    
    let totalCharCount = 0;
    const segmentLengths = rawSegments.map((s: string) => s.length);
    segmentLengths.forEach(l => totalCharCount += l);

    const timingMap: Array<{ start: number; end: number }> = [];
    let currentPct = 0;
    segmentLengths.forEach(len => {
        const startRange = currentPct;
        const endRange = startRange + (len / (totalCharCount || 1));
        timingMap.push({ start: startRange, end: endRange });
        currentPct = endRange;
    });

    transcriptEl!.innerHTML = rawSegments
        .map((chunk: string, index: number) => 
            `<p class="transcript-line" id="line-${index}">${chunk}</p>`
        )
        .join('');

    // =========================
    // AUDIO
    // =========================

    const audio = new Audio(data.audioUrl);

    // =========================
    // WAVEFORM
    // =========================

    if (waveform) {
        waveform.innerHTML = '';
        for (let i = 0; i < 60; i++) {
            const bar = document.createElement('div');
            bar.className = 'wave-bar';
            bar.style.height = `${10 + Math.random() * 25}px`;
            waveform.appendChild(bar);
        }
    }

    audio.addEventListener('loadedmetadata', () => {
        if (durationEl) durationEl.textContent = formatTime(audio.duration);
    });

    // =========================
    // EXTRA CONTROLS (SPEED/SKIP)
    // =========================
    
    const rewindBtn = document.getElementById('rewind');
    const forwardBtn = document.getElementById('forward');
    const speedControl = document.getElementById('speed-control');
    const speedText = document.getElementById('speed-text');

    rewindBtn?.addEventListener('click', () => {
        audio.currentTime = Math.max(0, audio.currentTime - 10);
        
        // Brief animation feedback
        rewindBtn.style.transform = 'scale(0.9)';
        setTimeout(() => rewindBtn.style.transform = 'scale(1)', 100);
    });

    forwardBtn?.addEventListener('click', () => {
        audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 10);
        
        // Brief animation feedback
        forwardBtn.style.transform = 'scale(0.9)';
        setTimeout(() => forwardBtn.style.transform = 'scale(1)', 100);
    });

    const speeds = [0.75, 1, 1.25, 1.5, 2];
    let speedIdx = 1; // Default 1x

    speedControl?.addEventListener('click', () => {
        speedIdx = (speedIdx + 1) % speeds.length;
        const newSpeed = speeds[speedIdx];
        
        audio.playbackRate = newSpeed;
        if (speedText) speedText.innerText = `${newSpeed}x Speed`;
        
        // Animated feedback
        speedControl.style.transform = 'translateY(-2px)';
        setTimeout(() => speedControl.style.transform = 'translateY(0)', 150);
    });

    // =========================
    // ANIMATION SYSTEM
    // =========================

    let animationId: number | null = null;

    function animateWaveform() {
        if (!isPlaying) {
            if (animationId) cancelAnimationFrame(animationId);
            return;
        }

        const bars = document.querySelectorAll('.wave-bar');
        const progress = (audio.currentTime / audio.duration) || 0;
        const activeBarsCount = Math.floor(progress * bars.length);

        bars.forEach((bar: any, index) => {
            const isActive = index <= activeBarsCount;
            
            if (isActive) {
                // SIGNIFICANT VARIANCES FOR TALLER HEIGHTS
                const baseHeight = 30;
                const variance = 90; // Increased peak height variance
                const randomFactor = Math.random() * variance;
                bar.style.height = `${baseHeight + randomFactor}px`;
                bar.classList.add('active');
            } else {
                // Background pulses slightly taller
                const base = 12;
                const variance = 10;
                bar.style.height = `${base + Math.random() * variance}px`;
                bar.classList.remove('active');
            }
        });

        animationId = requestAnimationFrame(animateWaveform);
    }

    // =========================
    // FOLLOW MODE
    // =========================

    let isFollowEnabled = true;
    const toggleFollowBtn = document.getElementById('toggle-follow');
    const followIcon = document.getElementById('follow-icon');
    const followText = document.getElementById('follow-text');

    toggleFollowBtn?.addEventListener('click', () => {
        isFollowEnabled = !isFollowEnabled;
        
        if (isFollowEnabled) {
            toggleFollowBtn.classList.add('active-toggle');
            followText!.innerText = 'Follow: ON';
            if (followIcon) followIcon.className = 'icon-eye';
            
            // Immediately scroll to current line
            const lines = document.querySelectorAll('.transcript-line');
            if (currentLineIndex !== -1 && lines[currentLineIndex]) {
                 lines[currentLineIndex].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                 });
            }
        } else {
            toggleFollowBtn.classList.remove('active-toggle');
            followText!.innerText = 'Follow: OFF';
            if (followIcon) followIcon.className = 'icon-eye-off';
        }
    });

    // =========================
    // PLAY STATE
    // =========================

    let isPlaying = false;

    playBtn?.addEventListener('click', () => {
        if (!isPlaying) {
            audio.play();
            isPlaying = true;
            playIcon!.className = 'icon-pause';
            animateWaveform();
        } else {
            audio.pause();
            isPlaying = false;
            playIcon!.className = 'icon-play';
            if (animationId) {
                cancelAnimationFrame(animationId);
                animationId = null;
            }
        }
    });

    // =========================
    // AUDIO UPDATE
    // =========================

    let currentLineIndex = -1;

    audio.addEventListener('timeupdate', () => {
        const progress = (audio.currentTime / audio.duration) * 100;

        // Update Progress Bar
        if (progressFill) progressFill.style.width = `${progress}%`;

        // Update Time Text
        if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);

        // Transcript Highlight Scroll
        const lines = document.querySelectorAll('.transcript-line');
        if (lines.length === 0) return;

        // Accurate Proportional Transcript Find
        const progressRatio = audio.currentTime / (audio.duration || 1);
        let activeLine = timingMap.findIndex(range => 
            progressRatio >= range.start && progressRatio < range.end
        );

        // End of file safety net
        if (activeLine === -1 && progressRatio >= 0.95) {
            activeLine = rawSegments.length - 1;
        }
        
        if (activeLine === -1) activeLine = 0;

        if (activeLine !== currentLineIndex && activeLine >= 0) {
            
            // Remove previous active state
            if (currentLineIndex !== -1 && lines[currentLineIndex]) {
                lines[currentLineIndex].classList.remove('active-line');
            }

            // Set new active state
            const line = lines[activeLine];
            if (line) {
                line.classList.add('active-line');
                
                // Only perform scroll INTO view if explicit toggle IS ACTIVE
                if (isFollowEnabled) {
                    line.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }

            currentLineIndex = activeLine;
        }
    });

    // =========================
    // SEEK
    // =========================

    progressContainer?.addEventListener(
        'click',
        (e: any) => {

            const rect =
                progressContainer.getBoundingClientRect();

            const percent =
                (e.clientX - rect.left) / rect.width;

            audio.currentTime =
                percent * audio.duration;
        });

    // =========================
    // FORMAT TIME
    // =========================

    function formatTime(seconds: number) {

        if (!seconds) return '00:00';

        const mins =
            Math.floor(seconds / 60);

        const secs =
            Math.floor(seconds % 60);

        return `${mins
            .toString()
            .padStart(2, '0')}:${secs
                .toString()
                .padStart(2, '0')}`;
    }
}

initPlayer();