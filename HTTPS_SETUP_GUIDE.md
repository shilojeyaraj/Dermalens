# HTTPS Setup Guide - Fix Camera Permission Issue

## Problem
Modern browsers require HTTPS to access the camera, even on localhost. Your app is running on HTTP, which blocks camera access.

## Quick Solutions

### Option 1: Use Chrome with Flags (Easiest)
1. Close all Chrome windows
2. Open Chrome with flags:
   ```bash
   chrome.exe --unsafely-treat-insecure-origin-as-secure=http://localhost:3000 --user-data-dir="C:\temp\chrome_dev"
   ```
3. Navigate to `http://localhost:3000`
4. Camera should now work

### Option 2: Use Firefox (Alternative)
Firefox is more lenient with localhost camera access:
1. Open Firefox
2. Go to `about:config`
3. Search for `media.navigator.permission.disabled`
4. Set to `true`
5. Navigate to `http://localhost:3000`

### Option 3: Use Edge with Flags
1. Close all Edge windows
2. Open Edge with flags:
   ```bash
   msedge.exe --unsafely-treat-insecure-origin-as-secure=http://localhost:3000 --user-data-dir="C:\temp\edge_dev"
   ```

### Option 4: Set up HTTPS (Recommended for Production)

#### For Next.js Frontend:
1. Install mkcert for local certificates:
   ```bash
   # Download from https://github.com/FiloSottile/mkcert/releases
   # Or use chocolatey: choco install mkcert
   ```

2. Generate certificates:
   ```bash
   mkcert -install
   mkcert localhost 127.0.0.1 ::1
   ```

3. Update package.json:
   ```json
   {
     "scripts": {
       "dev": "next dev",
       "dev:https": "next dev --experimental-https --experimental-https-key ./localhost-key.pem --experimental-https-cert ./localhost.pem"
     }
   }
   ```

4. Run with HTTPS:
   ```bash
   npm run dev:https
   ```

#### For FastAPI Backend:
1. Update CORS origins:
   ```python
   ALLOWED_ORIGINS = ["https://localhost:3000"]
   ```

2. Run with HTTPS:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=localhost-key.pem --ssl-certfile=localhost.pem
   ```

## Testing Steps

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser** with one of the solutions above:
   - Chrome with flags: `chrome.exe --unsafely-treat-insecure-origin-as-secure=http://localhost:3000`
   - Firefox with config change
   - Or use HTTPS setup

4. **Test Flow**:
   - Sign up → Profile setup → Scan page
   - Camera should now work
   - Or click "Skip for Now" to test profile-based recommendations

## What Happens Now

### With Camera Working:
- Live video feed appears
- 3-angle scanning works
- Full AI analysis with images

### With Skip (No Camera):
- Profile-based recommendations
- Products based on skin type and age
- AI-generated routine
- Still get valuable insights

## Troubleshooting

### Still Getting Camera Error:
1. Check browser console for specific error
2. Try different browser
3. Check if another app is using camera
4. Restart browser completely

### Backend Connection Issues:
1. Ensure backend is running on port 8000
2. Check CORS settings
3. Verify JWT token in localStorage

### Profile Recommendations Not Working:
1. Check if user completed profile setup
2. Verify database connection
3. Check backend logs for errors

## Production Deployment

For production, you'll need:
1. Real SSL certificates (Let's Encrypt)
2. Domain name
3. HTTPS configuration
4. Environment variables for production

## Summary

The easiest fix is using Chrome with the `--unsafely-treat-insecure-origin-as-secure` flag. This allows camera access on localhost HTTP for development.

For production, proper HTTPS setup is required.
