# Render Deployment with Docker

This guide covers deploying PatchHive to Render.com using Docker containers for improved reliability and consistency.

## 🚀 Quick Deploy

**One-Click Deployment:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above
2. Connect your GitHub account
3. Select the PatchHive repository
4. Render will automatically detect `render.yaml`
5. Click "Apply" to deploy all services
6. Wait ~10-15 minutes for initial build

## 📋 What Gets Deployed

### Database
- **PostgreSQL 15** (free tier)
- Database name: `patchhive`
- Automatic connection string injection to backend

### Backend API
- **Docker container** with Python 3.11
- FastAPI + Uvicorn server
- Automatic database migrations on startup
- Health check endpoint: `/health`
- URL: `https://patchhive-api.onrender.com`

### Frontend
- **Docker container** with Nginx
- React + Vite production build
- SPA routing configured
- Static asset caching
- Health check endpoint: `/health`
- URL: `https://patchhive-frontend.onrender.com`

## 🔧 Configuration Files

### Dockerfiles

**Dockerfile.backend** (Root directory)
- Multi-stage Python build
- Installs system dependencies
- Copies backend code
- Runs uvicorn on port 10000

**Dockerfile.frontend** (Root directory)
- Multi-stage Node build
- Builds Vite production bundle
- Serves with Nginx on port 8080
- Includes health check endpoint

### render.yaml

Located at project root, defines:
- 1 PostgreSQL database
- 2 web services (backend + frontend)
- Environment variables
- Health check paths
- Auto-deploy settings

## 🌐 Environment Variables

### Backend (Auto-configured)

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | From database | PostgreSQL connection string |
| `SECRET_KEY` | Auto-generated | JWT signing key |
| `CORS_ORIGINS` | Set in config | Frontend URL for CORS |
| `PORT` | Render | Service port (10000) |

### Frontend (Auto-configured)

| Variable | Source | Description |
|----------|--------|-------------|
| `VITE_API_URL` | Set in config | Backend API URL |
| `PORT` | Render | Service port (8080) |

## ✅ Post-Deployment Verification

### 1. Check Service Status

Go to [Render Dashboard](https://dashboard.render.com)
- All 3 services should show "Live" status
- Database should show "Available"

### 2. Test Backend API

```bash
curl https://patchhive-api.onrender.com/health
# Expected: {"status":"healthy"}

curl https://patchhive-api.onrender.com/
# Expected: {"message":"Welcome to PatchHive API",...}
```

### 3. Test Frontend

```bash
curl -I https://patchhive-frontend.onrender.com/health
# Expected: HTTP/1.1 200 OK

curl -I https://patchhive-frontend.onrender.com/
# Expected: HTTP/1.1 200 OK
```

### 4. Check Database Tables

Database tables are automatically created on first backend startup.

View logs:
```bash
# In Render Dashboard:
# patchhive-api -> Logs
# Look for: "Database initialized" or similar
```

## 🔍 Troubleshooting

### Issue: Backend shows 503 Service Unavailable

**Cause:** Service is still building or starting up

**Solution:**
- Wait 2-3 minutes after deployment
- Check logs in Render Dashboard
- First cold start takes ~30 seconds

### Issue: Frontend shows blank page

**Cause:** Frontend can't reach backend (CORS error)

**Solution:**
1. Check browser console for errors
2. Verify CORS_ORIGINS in backend includes frontend URL
3. Update in Render Dashboard: Settings -> Environment
4. Redeploy backend service

### Issue: Database connection error

**Cause:** DATABASE_URL not properly set

**Solution:**
1. Go to Render Dashboard
2. patchhive-api -> Environment
3. Verify DATABASE_URL is present
4. Should start with: `postgresql://patchhive:...`

### Issue: Build fails

**Cause:** Missing dependencies or syntax errors

**Solution:**
1. Check Render build logs
2. Common fixes:
   - Ensure `requirements.txt` is up to date
   - Ensure `package-lock.json` is committed
   - Check Dockerfile syntax

## 📊 Performance & Limits

### Free Tier Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| **Services** | Unlimited | But limited resources |
| **Build minutes** | 500/month | Shared across all services |
| **Bandwidth** | 100 GB/month | Per service |
| **Storage** | 1 GB | Database |
| **Spinning down** | After 15min | Cold start ~30s |

### Performance Tips

**Backend:**
- First request after spin-down: ~30 seconds
- Subsequent requests: <100ms
- Database queries: <50ms

**Frontend:**
- Nginx serves static files efficiently
- Gzip compression enabled
- Asset caching configured

## 🔄 Updates & Redeploys

### Automatic Deploys

With `autoDeploy: true` in render.yaml:
- Push to main branch → Auto redeploys
- Pull request merge → Auto redeploys

### Manual Deploys

In Render Dashboard:
1. Select service
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

### Rollback

1. Go to service in Dashboard
2. Click "Deploys" tab
3. Find previous working deploy
4. Click "Rollback to this deploy"

## 💰 Cost Optimization

### Stay on Free Tier

- ✅ Use free tier for all services
- ✅ Services spin down after 15 min
- ✅ Keep data under 1 GB
- ✅ Monitor bandwidth usage

### Upgrade for Production

**Starter Plan (~$7/service)**
- No spinning down
- Always available
- Better performance
- More resources

**Total cost for production:** ~$21/month
- Backend: $7/month
- Frontend: $7/month
- Database: $7/month

## 🔒 Security Checklist

- [x] HTTPS enabled (automatic)
- [x] SECRET_KEY auto-generated
- [x] Database credentials secure
- [x] CORS properly configured
- [x] No secrets in repository
- [x] Environment variables encrypted

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Docker Docs](https://render.com/docs/docker)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [PatchHive Deployment Options](DEPLOYMENT_OPTIONS.md)

## 🆘 Support

**Having issues?**

1. Check [Troubleshooting](#troubleshooting) section
2. View Render logs in Dashboard
3. Verify all files are committed to main branch
4. Check [GitHub Issues](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues)

---

**Status: Ready to deploy with Docker! 🐳**
