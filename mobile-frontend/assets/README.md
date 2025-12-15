# Assets Directory

This directory contains app assets such as icons and splash screens.

## Required Assets

The following assets should be added before building for production:

- `icon.png` - App icon (1024x1024px)
- `splash.png` - Splash screen image
- `adaptive-icon.png` - Android adaptive icon foreground (1024x1024px)
- `favicon.png` - Web favicon (48x48px)

## Development Note

For development purposes, Expo will use default placeholder assets if these files are not present.
The app will function normally in development mode without custom assets.

## Generating Assets

You can use `expo-splash-screen` and similar tools to generate properly sized assets from your source images.
