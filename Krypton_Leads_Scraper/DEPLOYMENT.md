# 🚀 Vercel + Railway Deployment Guide

**Cost: ~$5/month** (vs Render's $25+)

## 🎯 Quick Setup (5 minutes)

### 1. **Frontend: Deploy to Vercel**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (from root directory)
vercel --prod
```

**Or use Vercel Dashboard:**
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Deploy automatically

### 2. **Backend: Deploy to Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

**Or use Railway Dashboard:**
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Connect GitHub repo
4. Add PostgreSQL + Redis services

## 🔧 Environment Variables

### **Vercel (Frontend)**
Add in Vercel dashboard:

```
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=generate-32-char-secret
BACKEND_URL=https://your-backend.up.railway.app
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### **Railway (Backend)**
Add in Railway dashboard:

```
JWT_SECRET=your-jwt-secret
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

*Note: Railway auto-provides DATABASE_URL and REDIS_URL*

## 📊 Services Setup

### **Railway Services:**
1. **Web Service** (FastAPI backend)
2. **PostgreSQL** (database)
3. **Redis** (caching)

Total cost: **$5-8/month**

### **Vercel:**
- **Free tier** handles most traffic
- Auto-scaling and CDN included

## 🔗 Custom Domains

### **Vercel:**
1. Add domain in Vercel dashboard
2. Update DNS records
3. SSL auto-configured

### **Railway:**
1. Add custom domain in Railway
2. Update BACKEND_URL in Vercel env vars

## 🛠️ Local Development

```bash
# Frontend
npm run dev

# Backend  
cd backend
uvicorn main:app --reload --port 8000
```

## 🚀 Auto-Deploy

Both platforms auto-deploy on git push to main branch.

## 💰 Pricing Comparison

| Service | Render | **Vercel + Railway** |
|---------|--------|---------------------|
| Frontend | $7/month | **Free** |
| Backend | $25/month | **$5/month** |
| Database | $25/month | **$5/month** |
| Redis | $10/month | **$3/month** |
| **Total** | **$67/month** | **$13/month** |

**Savings: $650/year** 💰

## 🔍 Monitoring

### **Vercel:**
- Built-in analytics
- Performance monitoring
- Error tracking

### **Railway:**
- Resource usage graphs
- Logs and metrics
- Uptime monitoring

## 🆘 Troubleshooting

**Common issues:**

1. **Build fails:** Check `package.json` scripts
2. **DB connection:** Verify DATABASE_URL format
3. **CORS errors:** Update allowed origins in backend
4. **Environment vars:** Double-check all variables are set

**Support:**
- Vercel: Excellent docs + community
- Railway: Discord community + fast support

---

**Ready to deploy? This setup is 5x cheaper and more reliable than Render!**