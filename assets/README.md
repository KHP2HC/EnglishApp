# Assets

This directory contains bundled assets for EnglishCoach Pro.

## Structure

```
assets/
├── fonts/       # Bundled fonts (Outfit, Inter, JetBrains Mono)
├── icons/       # UI icons (SVG/PNG)
└── audio/       # Sample audio clips
```

## Fonts

The app uses the following fonts (fall back to system defaults if not bundled):
- **Headlines**: Outfit (Bold, 700)
- **Body**: Inter or system default
- **Code/Phonetics**: JetBrains Mono

## Icons

Emoji are used as primary icons for approachability. Additional SVG/PNG
icons can be placed in `icons/` for custom UI elements.

## Audio

Sample audio clips for listening exercises can be placed in `audio/`.
The app also generates TTS audio on-the-fly using edge-tts.
