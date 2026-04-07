# The Culinary Index - Mobile App (Capacitor)

This directory contains the Capacitor configuration for building native Android and iOS apps that load your deployed web app.

## Prerequisites

- Node.js 18+
- Java JDK 17+ (for Android)
- Android Studio (for Android builds)
- Xcode (for iOS builds, macOS only)

## Quick Start

```bash
cd mobile
npm install
```

## Android

```bash
npx cap add android
npx cap sync android
npx cap open android
```

This opens Android Studio. From there:
1. Build → Build Bundle(s) / APK(s) → Build APK (for testing)
2. Build → Build Bundle(s) / APK(s) → Build Bundle (for Play Store)
3. The APK will be in `android/app/build/outputs/apk/debug/`
4. The AAB will be in `android/app/build/outputs/bundle/release/`

## iOS (macOS only)

```bash
npx cap add ios
npx cap sync ios
npx cap open ios
```

This opens Xcode. From there:
1. Select your team for signing
2. Product → Archive
3. Distribute to App Store

## How It Works

The app loads `https://culinary-index.onrender.com` inside a native WebView. All updates to your website are reflected instantly — no app update needed.

## Configuration

See `capacitor.config.json`:
- `server.url` — your deployed web app URL
- `server.allowNavigation` — domains the WebView can navigate to
- `appId` — the package identifier (used in app stores)
- `appName` — the name shown under the app icon

## Building for Release

### Android APK (for testing/sideloading)
```bash
cd android
./gradlew assembleDebug
# APK at: app/build/outputs/apk/debug/app-debug.apk
```

### Android AAB (for Google Play)
```bash
cd android
./gradlew bundleRelease
# AAB at: app/build/outputs/bundle/release/app-release.aab
```

## Updating the App

Since the app loads a remote URL, you only need to rebuild if you change:
- `capacitor.config.json`
- Native plugins
- App icon or splash screen

Website changes are reflected instantly.
