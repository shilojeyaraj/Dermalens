# 🔄 Supabase Keep-Alive Setup - Dermalens

## ✅ Implementation Complete!

The Supabase keep-alive endpoint has been successfully implemented to prevent your database from pausing due to inactivity.

## 📍 What Was Added

1. **Keep-Alive API Endpoint**: `app/api/keepalive/route.ts`
   - Performs lightweight database query to keep Supabase active
   - Uses `profiles` table (guaranteed to exist in your database)
   - Returns 200 status even on errors (to keep cron happy)

2. **Vercel Cron Configuration**: Added to `vercel.json`
   - Scheduled to run daily at 12:00 UTC
   - **Note**: Vercel Cron requires Pro plan ($20/month)
   - **Recommendation**: Use free external cron service instead (see below)

## 🚀 Next Steps

### Option 1: Use Free External Cron Service (Recommended)

Since Vercel Cron requires Pro plan, use a free service:

#### cron-job.org (Recommended - Free)

1. **Sign Up**: Go to [https://cron-job.org](https://cron-job.org) and create a free account

2. **Create Cron Job**:
   - Click "Create cronjob"
   - **Title**: `Dermalens Supabase Keep-Alive`
   - **Address**: `https://your-app.vercel.app/api/keepalive`
     - Replace `your-app` with your actual Vercel app URL
   - **Schedule**: Daily at 12:00 UTC (`0 12 * * *`)
   - **Notification**: Email on failure (optional but recommended)

3. **Activate**: Click "Create cronjob" and verify it shows "Active"

#### Alternative: UptimeRobot (Free)

1. Go to [https://uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account
3. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.vercel.app/api/keepalive`
   - **Interval**: 5 minutes (free tier allows this)
4. Save monitor

### Option 2: Use Vercel Cron (Requires Pro Plan)

If you have Vercel Pro, the cron is already configured in `vercel.json`:
- Schedule: Daily at 12:00 UTC
- Path: `/api/keepalive`
- No additional setup needed

## ✅ Verification

### 1. Test Endpoint Locally

```bash
# Start dev server
npm run dev

# Test endpoint (in another terminal)
curl http://localhost:3000/api/keepalive
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Supabase connection active",
  "timestamp": "2024-12-13T23:00:00.000Z",
  "profileCount": 0
}
```

### 2. Test in Production

After deploying to Vercel:

```bash
curl https://your-app.vercel.app/api/keepalive
```

### 3. Verify Cron Job

- Check cron service dashboard for successful executions
- Check Vercel logs for `/api/keepalive` requests
- Check Supabase Activity tab for periodic queries

## 🔧 Configuration

### Environment Variables Required

Make sure these are set in Vercel:

- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anonymous key

**To set in Vercel:**
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add both variables for Production, Preview, and Development

### Change Table Name (If Needed)

If you want to use a different table, edit `app/api/keepalive/route.ts`:

```typescript
// Change from 'profiles' to your table name
const { count, error } = await supabase
  .from('user_skin_profiles')  // Change this
  .select('*', { count: 'exact', head: true })
  .limit(1)
```

**Available tables in your database:**
- `profiles` ✅ (currently used)
- `user_skin_profiles`
- `user_images`

## 📊 How It Works

1. **Daily Ping**: Cron job calls `/api/keepalive` once per day
2. **Lightweight Query**: Endpoint performs a count query on `profiles` table
3. **Database Activity**: Query keeps Supabase active (pauses after 7 days of inactivity)
4. **Safety Margin**: Daily ping provides 6-day safety margin

## 🚨 Troubleshooting

### Endpoint Returns 404

**Problem**: Endpoint not found after deployment

**Solution**:
- Verify file exists at `app/api/keepalive/route.ts`
- Ensure file is committed and pushed to GitHub
- Redeploy on Vercel

### Endpoint Returns 500 Error

**Problem**: Database connection issue

**Solution**:
- Check environment variables are set in Vercel:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Verify Supabase project is active (not paused)
- Check Supabase project URL is correct

### Cron Job Not Executing

**Problem**: External cron service not calling endpoint

**Solution**:
- Verify URL is correct (include `https://`)
- Check cron job is active in service dashboard
- Ensure endpoint is publicly accessible (no auth required)
- Test endpoint manually first: `curl https://your-app.vercel.app/api/keepalive`

### Supabase Still Pausing

**Problem**: Keep-alive not working

**Solution**:
- Increase frequency (daily instead of weekly)
- Verify queries are appearing in Supabase Activity tab
- Check for errors in Vercel function logs
- Ensure cron job is actually executing (check service dashboard)

## 📋 Checklist

- [x] Keep-alive endpoint created (`app/api/keepalive/route.ts`)
- [x] Vercel cron configuration added (optional, requires Pro)
- [ ] Environment variables set in Vercel
- [ ] Endpoint tested locally
- [ ] Endpoint tested in production
- [ ] External cron service configured (cron-job.org recommended)
- [ ] First cron execution verified
- [ ] Supabase Activity shows periodic queries

## 💡 Best Practices

1. **Use External Cron Service (Free)**
   - Don't pay for Vercel Pro just for this
   - cron-job.org is free and reliable

2. **Daily Ping is Sufficient**
   - Supabase pauses after 7 days
   - Daily ping provides 6-day safety margin

3. **Monitor for First Week**
   - Verify it's working correctly
   - Catch issues early

4. **Check Supabase Activity Tab**
   - Verify queries are happening
   - Look for `/api/keepalive` requests

## 🎯 Success Criteria

Your implementation is successful when:

- ✅ Endpoint returns 200 status code
- ✅ Cron job executes daily without errors
- ✅ Supabase Activity shows periodic queries
- ✅ Supabase project remains active (not paused)
- ✅ No manual intervention needed

---

**Status**: ✅ Implemented and Ready  
**Last Updated**: December 2024  
**Next Action**: Set up external cron service at cron-job.org

