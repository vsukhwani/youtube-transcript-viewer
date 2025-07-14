# Deploying YouTube Transcript Viewer to Vercel

This guide walks you through deploying the YouTube Transcript Viewer application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Git](https://git-scm.com/downloads) installed
3. The [Vercel CLI](https://vercel.com/download) (optional, but recommended)

## Deployment Steps

### 1. Push your code to GitHub

If you haven't already, push your code to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/youtube-transcript-viewer.git
git push -u origin main
```

### 2. Deploy using the Vercel Dashboard

**Option A: Deploy directly from GitHub**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" > "Project"
3. Import your GitHub repository
4. Configure the project:
   - Root Directory: Keep as default (the repository root)
   - Build Command: Leave blank (Vercel will auto-detect)
   - Output Directory: Leave blank (Vercel will auto-detect)
5. Click "Deploy"

**Option B: Deploy using Vercel CLI**

1. Install Vercel CLI if you haven't already:
   ```bash
   npm i -g vercel
   ```

2. Navigate to your project directory and run:
   ```bash
   vercel
   ```

3. Follow the prompts to configure your deployment

### 3. Verify the deployment

After deployment:

1. Vercel will provide you with a URL for your deployed application
2. Open the URL and test that the transcript viewer works
3. Try fetching a transcript for one of the test videos

## Important Configuration Files

The application is configured to work on Vercel through these key files:

- **`vercel.json`**: Configures Vercel serverless functions
- **`api/transcript_v2.py`**: The serverless function for transcript fetching
- **`api/requirements.txt`**: Dependencies for the serverless function
- **`frontend/config.js`**: Automatically detects the environment and uses the appropriate API URL

## Troubleshooting

If you encounter issues:

1. Check Vercel deployment logs in the Vercel Dashboard
2. Ensure all required dependencies are listed in `api/requirements.txt`
3. Verify that `vercel.json` is properly configured
4. Check that `frontend/config.js` is correctly detecting the environment

## Custom Domain (Optional)

To use a custom domain:

1. Go to your project in the Vercel Dashboard
2. Click "Settings" > "Domains"
3. Add your custom domain and follow the verification steps
