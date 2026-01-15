# How to Share Your Application

To share your application on WhatsApp or Email, you need a **public link**. Since your app runs on your computer, others can't see it unless you "deploy" it to the internet.

Here are the two best ways to do this:

## Option 1: Permanent Deployment (Recommended)
This gives you a permanent URL (e.g., `yourapp.onrender.com`) that is perfect for sharing. We will use **Render** (free tier).

### 1. Preparation (Already Done)
I have already added the necessary files to your project:
- `Procfile`: Tells the server how to run your app.
- `requirements.txt`: Added `gunicorn` and `eventlet` for production.

### 2. Push to GitHub
1. Create a new repository on [GitHub](https://github.com/new).
2. Push your code to this repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   # Replace URL with your new repo URL
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git 
   git push -u origin main
   ```

### 3. Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render will detect the `Procfile` automatically.
5. **CRITICAL:** Scroll down to **Environment Variables** and add your secrets from your `.env` file:
   - `SUPABASE_URL`: (Copy value from your .env)
   - `SUPABASE_KEY`: (Copy value from your .env)
   - `SECRET_KEY`: generalink-secret-key (or generated new one)
6. Click **Create Web Service**.

Wait a few minutes, and Render will give you a URL like `https://project-name.onrender.com`. copy and paste this into WhatsApp!

---

## Option 2: Temporary Link (Fastest)
If you just want to show someone *right now* and don't want to set up GitHub/Render, use **ngrok**. The link will expire when you close your terminal.

1. Download [ngrok](https://ngrok.com/download) and unzip it.
2. Open a terminal in your project folder.
3. Start your app:
   ```bash
   python app.py
   ```
4. Open a **second** terminal and run:
   ```bash
   ngrok http 5000
   ```
5. Copy the `https://....ngrok-free.app` link and share it.
