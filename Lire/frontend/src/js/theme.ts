/**
 * Lire Theme Management
 * Handles dark/light mode and state persistence
 */

export function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const icon = themeToggle?.querySelector('i');

    const savedTheme = localStorage.getItem('lire-theme') || 'light';
    applyTheme(savedTheme);

    themeToggle?.addEventListener('click', () => {
        const currentTheme = html.classList.contains('dark') ? 'light' : 'dark';
        applyTheme(currentTheme);
        localStorage.setItem('lire-theme', currentTheme);
    });

    function applyTheme(theme: string) {
        if (theme === 'dark') {
            html.classList.remove('light');
            html.classList.add('dark');
            if (icon) {
                icon.className = 'lucide-moon';
            }
        } else {
            html.classList.remove('dark');
            html.classList.add('light');
            if (icon) {
                icon.className = 'lucide-sun';
            }
        }
    }
}

// Auto-init for non-module usage if needed, but since we use modules:
initTheme();
