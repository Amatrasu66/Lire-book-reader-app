/**
 * Lire Advanced Animations
 * Handles scroll-triggers and persistent ambience
 */

export function initAnimations() {
    // Add intersection observer for reveal effects
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.glass-card').forEach(card => {
        observer.observe(card);
    });

    // Parallax effect on header or background if desired
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const orbs = document.querySelectorAll('.orb');
        orbs.forEach((orb, idx) => {
            const speed = (idx + 1) * 0.1;
            (orb as HTMLElement).style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

initAnimations();
