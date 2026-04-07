# Deploy to PythonAnywhere (100% Free)

## Step 1: Create Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **Start running Python in the cloud now**
3. Choose **Beginner account** (free)
4. Pick a username (e.g., `axelodo7`)

## Step 2: Upload Your Code
1. In the PythonAnywhere dashboard, go to **Consoles** → **Bash**
2. Run these commands:
```bash
git clone https://github.com/Axelodo7/Culinary-Index.git
cd CulinaryIndex
pip3.12 install --user flask gunicorn requests beautifulsoup4 ddgs lxml
```

## Step 3: Create the Web App
1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (NOT the Flask wizard)
4. Choose **Python 3.12**
5. Click **Next**

## Step 4: Configure the Web App
In the **Code** section:
- **Source code**: `/home/YOUR_USERNAME/CulinaryIndex`
- **Working directory**: `/home/YOUR_USERNAME/CulinaryIndex`

In the **WSGI configuration file** section:
- Click the link to edit the WSGI file
- Replace ALL content with the content from `pythonanywhere_wsgi.py`
- Replace `YOUR_USERNAME` with your actual PythonAnywhere username
- Save

## Step 5: Configure Virtual Environment (Optional but Recommended)
In the **Virtualenv** section:
```
/home/YOUR_USERNAME/.local
```

## Step 6: Reload
Click the green **Reload** button at the top.

Your app is now live at: `https://YOUR_USERNAME.pythonanywhere.com`

## Step 7: Update Mobile App
Edit `mobile/capacitor.config.json`:
```json
"url": "https://YOUR_USERNAME.pythonanywhere.com"
```

Then rebuild:
```bash
cd mobile
npx cap sync android
cd android
.\gradlew.bat assembleDebug
.\gradlew.bat installDebug
```

## Important Notes
- **Free accounts must log in monthly** to keep the app active
- **100 CPU seconds/day** limit (enough for normal usage)
- **No custom domains** on free tier
- **HTTPS is automatic**
