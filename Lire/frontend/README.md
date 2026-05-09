# Lire Frontend

This is the complete frontend implementation for Lire, an AI-powered reading-to-audio productivity tool.

## Structure
- `index.html`: Landing page and Upload Workspace.
- `player.html`: Immersive Audio Player.
- `css/`: Theme-aware styles (themes, animations, styles, responsive).
- `src/js/`: Vanilla TypeScript logic for UI interactions and simulated backend integration.

## Features
- **Modern UI**: Clean, minimalist design with focus on typography and spacing.
- **Theming**: Integrated Dark/Light mode support.
- **Upload**: Interactive drag-and-drop file upload with validation.
- **Audio Player**: Custom playback controls with a dynamic waveform visualizer.
- **Animations**: Subtle premium transitions and floating effects.

## Backend Integration
The `upload.ts` file is prepared for integration with a Flask backend. It includes a `simulateUpload` function that can be easily replaced with a real `fetch` call to `http://127.0.0.1:5000/upload`.
