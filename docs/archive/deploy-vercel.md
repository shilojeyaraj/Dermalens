# Quick Vercel Deployment Guide

## 🚀 Deploy in 3 Steps

### Step 1: Connect Repository to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub/GitLab/Bitbucket repository
3. Vercel will auto-detect Next.js

### Step 2: Configure Project Settings

In the Vercel dashboard:
- **Root Directory:** `frontend`
- **Framework Preset:** Next.js (auto-detected)
- **Build Command:** Leave empty (auto-detected)
- **Output Directory:** Leave empty (auto-detected)

### Step 3: Add Environment Variables

Go to **Settings → Environment Variables** and add:

```
NEXT_PUBLIC_API_URL=https://dermalens-backend-941238576063.us-central1.run.app
NEXT_PUBLIC_SUPABASE_URL=https://ezlevlxkxanlceofykrh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key-here
```

### Step 4: Deploy!

Click **Deploy** and wait for the build to complete.

Your app will be live at: `https://your-project.vercel.app`

---

## 📋 Using Vercel CLI (Alternative)

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd /path/to/Dermalens

# Login
vercel login

# Deploy (first time)
vercel

# Add environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production

# Deploy to production
vercel --prod
```

---

## ✅ What's Configured

- ✅ `vercel.json` - Root configuration pointing to `frontend` directory
- ✅ `frontend/vercel.json` - Next.js specific settings
- ✅ `frontend/next.config.js` - Updated for Vercel (removed standalone output)
- ✅ `.vercelignore` - Excludes unnecessary files from deployment
- ✅ Build scripts in `package.json`

---

## 🔧 Troubleshooting

**Build fails?**
- Check that `rootDirectory` is set to `frontend` in Vercel dashboard
- Verify all environment variables are set
- Check build logs in Vercel dashboard

**API not connecting?**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings on backend
- Ensure backend is accessible from internet

**Images not loading?**
- Check `next.config.js` has correct image domains
- Verify images use HTTPS URLs

---

For detailed instructions, see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

