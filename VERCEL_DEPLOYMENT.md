# Vercel Deployment Guide for Dermalens

This guide will help you deploy the Dermalens frontend to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. GitHub/GitLab/Bitbucket repository with your code
3. Backend API deployed and accessible (currently on Google Cloud Run)

## Quick Start

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect your repository:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub/GitLab/Bitbucket repository
   - Select the repository containing this project

2. **Configure the project:**
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (or leave empty for auto-detection)
   - **Output Directory:** `.next` (auto-detected)
   - **Install Command:** `npm install` (auto-detected)

3. **Set Environment Variables:**
   Go to Project Settings → Environment Variables and add:

   ```
   NEXT_PUBLIC_API_URL=https://dermalens-backend-941238576063.us-central1.run.app
   NEXT_PUBLIC_SUPABASE_URL=https://ezlevlxkxanlceofykrh.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key-here
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

4. **Deploy:**
   ```bash
   vercel
   ```

5. **Set environment variables:**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   # Enter: https://dermalens-backend-941238576063.us-central1.run.app
   
   vercel env add NEXT_PUBLIC_SUPABASE_URL
   # Enter: https://ezlevlxkxanlceofykrh.supabase.co
   
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
   # Enter: your-supabase-anon-key
   ```

6. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://dermalens-backend-941238576063.us-central1.run.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://ezlevlxkxanlceofykrh.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIs...` |

### Optional Variables

See `frontend/env.example` for a complete list of optional environment variables.

## Project Structure

```
Dermalens/
├── frontend/          # Next.js frontend (deployed to Vercel)
│   ├── app/          # Next.js app directory
│   ├── components/   # React components
│   ├── lib/          # Utilities and helpers
│   └── public/       # Static assets
├── apps/api/         # Backend API (deployed separately to Cloud Run)
└── vercel.json       # Vercel configuration (root level)
```

## Configuration Files

### `vercel.json` (Root)
- Configures Vercel to build from the `frontend` directory
- Sets up API rewrites and headers
- Configures function timeouts

### `frontend/vercel.json`
- Framework-specific configuration
- Function timeout settings

### `frontend/next.config.js`
- Next.js configuration
- Image domain settings
- Webpack configuration

## Build Process

1. Vercel installs dependencies (`npm install`)
2. Builds the Next.js app (`npm run build`)
3. Optimizes and deploys the application
4. Sets up edge functions and API routes

## Custom Domain

To use a custom domain:

1. Go to Project Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions
4. Vercel will automatically provision SSL certificates

## Environment-Specific Deployments

Vercel supports three environments:
- **Production:** `vercel --prod` or main branch
- **Preview:** Automatic for pull requests
- **Development:** `vercel dev` for local development

## Troubleshooting

### Build Fails

1. **Check build logs** in Vercel dashboard
2. **Verify Node.js version** (should be 18.x or 20.x)
3. **Check environment variables** are set correctly
4. **Review `next.config.js`** for any issues

### API Connection Issues

1. **Verify `NEXT_PUBLIC_API_URL`** is set correctly
2. **Check CORS settings** on your backend
3. **Verify backend is accessible** from Vercel's servers
4. **Check network tab** in browser DevTools

### Image Loading Issues

1. **Verify image domains** in `next.config.js`
2. **Check `remotePatterns`** configuration
3. **Ensure images are using HTTPS**

## Performance Optimization

Vercel automatically provides:
- ✅ Edge Network (CDN)
- ✅ Automatic HTTPS
- ✅ Image Optimization
- ✅ Serverless Functions
- ✅ Analytics
- ✅ Preview Deployments

## Monitoring

- **Vercel Analytics:** Built-in analytics dashboard
- **Logs:** View real-time logs in Vercel dashboard
- **Speed Insights:** Performance monitoring

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Set up environment variables
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring and analytics
5. ✅ Configure CI/CD for automatic deployments

---

**Note:** The backend API should remain deployed on Google Cloud Run or your preferred backend hosting solution. Vercel is only deploying the Next.js frontend.

