# Build The Culinary Index as an Android App (TWA)

## Prerequisites

- Node.js 18+ installed
- Java JDK 17+ installed
- Android SDK installed (via Android Studio)
- Google Play Developer account ($25 one-time fee)

## Step 1: Install Bubblewrap

```bash
npm install -g @bubblewrap/cli
```

## Step 2: Initialize TWA Project

```bash
cd twa
bubblewrap init --manifest https://culinary-index.onrender.com/manifest.json
```

When prompted:
- **Package ID**: `com.culinaryindex.app`
- **App name**: `The Culinary Index`
- **Launcher name**: `CulinaryIndex`
- **URL**: `https://culinary-index.onrender.com`
- **Icon**: Download from `https://culinary-index.onrender.com/static/icon-512.png`

## Step 3: Build the App

```bash
bubblewrap build
```

This generates:
- `android/app/build/outputs/bundle/release/app-release.aab` (for Play Store)
- `android/app/build/outputs/apk/release/app-release.apk` (for sideloading)

## Step 4: Upload to Google Play

1. Go to [Google Play Console](https://play.google.com/console)
2. Create a new app → "The Culinary Index"
3. Fill in store listing (description, screenshots, privacy policy)
4. Go to **Production** → **Create new release**
5. Upload the `.aab` file
6. Submit for review (takes 1-7 days)

## Alternative: Build with Android Studio

If Bubblewrap doesn't work:

1. Open `android/` folder in Android Studio
2. Sync Gradle
3. Build → Generate Signed Bundle / APK
4. Upload the `.aab` to Play Console

## Testing Locally

```bash
bubblewrap doctor          # Check environment
bubblewrap build --apk     # Build APK for testing
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

## Notes

- TWA uses Chrome's rendering engine — no URL bar, feels native
- Your deployed URL must be HTTPS (Render provides this)
- The app automatically gets the PWA manifest and service worker
- Updates to your website are reflected instantly (no app update needed)
