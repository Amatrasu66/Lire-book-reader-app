/**
 * Lire Main Entry
 * Orchestrates module loading and global states
 */

console.log('Lire Frontend initialized.');

// This can serve as a central registry for shared states (e.g. current user, current audio URL)
export const LireState = {
    user: null,
    currentTrack: null,
    isProcessing: false
};
