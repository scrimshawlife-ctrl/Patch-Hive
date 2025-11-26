# Azure Deployment Guide for PatchHive

Complete guide for deploying PatchHive to Microsoft Azure using Azure App Service, Static Web Apps, and PostgreSQL Flexible Server.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Quick Deploy](#quick-deploy)
- [Manual Deployment](#manual-deployment)
- [Configuration](#configuration)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- [Cost Estimation](#cost-estimation)

---

## 🎯 Prerequisites

### Required Tools

1. **Azure CLI** - [Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
   ```bash
   # Verify installation
   az --version

   # Login to Azure
   az login
   ```

2. **Azure Developer CLI (azd)** - [Install Guide](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
   ```bash
   # Verify installation
   azd version
   ```

3. **Git** - For repository access

### Azure Subscription

- Active Azure subscription ([Free tier available](https://azure.microsoft.com/free/))
- Sufficient permissions to create resources
- Resource providers registered:
  - Microsoft.Web
  - Microsoft.DBforPostgreSQL
  - Microsoft.Insights

---

## 🏗️ Architecture Overview

### Azure Resources Created

```
┌─────────────────────────────────────────────────────────────┐
│                      Resource Group                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  Frontend (Azure Static Web Apps)                      │ │
│  │  • React/Vite application                              │ │
│  │  • Free tier (100 GB bandwidth/month)                  │ │
│  │  • Custom domain support                               │ │
│  │  • Automatic SSL                                       │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           │ HTTPS                            │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  Backend API (Azure App Service)                       │ │
│  │  • Python 3.11 runtime                                 │ │
│  │  • FastAPI/Uvicorn                                     │ │
│  │  • Linux container                                     │ │
│  │  • B1 tier (1.75 GB RAM)                               │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           │ PostgreSQL Protocol              │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  Database (Azure PostgreSQL Flexible Server)           │ │
│  │  • PostgreSQL 15                                       │ │
│  │  • Burstable B1ms (2 vCores, 2 GB RAM)                │ │
│  │  • 32 GB storage                                       │ │
│  │  • 7-day backup retention                              │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Resource Details

| Resource | Type | Purpose | Tier |
|----------|------|---------|------|
| **patchhive-{env}-web** | Static Web App | React frontend | Free |
| **patchhive-{env}-api** | App Service | FastAPI backend | B1 |
| **patchhive-{env}-plan** | App Service Plan | Hosting plan | B1 Linux |
| **patchhive-{env}-db** | PostgreSQL Flexible Server | Database | Burstable B1ms |

---

## 🚀 Quick Deploy

### Option 1: Azure Developer CLI (Recommended)

The fastest way to deploy PatchHive to Azure:

```bash
# 1. Clone the repository
git clone https://github.com/scrimshawlife-ctrl/Patch-Hive.git
cd Patch-Hive

# 2. Initialize Azure Developer CLI
azd init

# 3. Provision and deploy all resources
azd up
```

**What happens:**
1. Prompts for Azure subscription and region
2. Creates resource group
3. Provisions PostgreSQL database
4. Deploys backend to App Service
5. Deploys frontend to Static Web Apps
6. Configures environment variables
7. Returns URLs for frontend and backend

**Estimated time:** 10-15 minutes

### Option 2: Azure Portal (One-Click)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fscrimshawlife-ctrl%2FPatch-Hive%2Fmain%2Finfra%2Fmain.bicep)

1. Click the button above
2. Fill in required parameters
3. Click "Review + create"
4. Wait for deployment to complete (~10 minutes)

---

## 🔧 Manual Deployment

### Step 1: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="patchhive-rg"
LOCATION="eastus"  # or your preferred region
ENVIRONMENT="dev"  # dev, staging, or prod

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 2: Generate Database Password

```bash
# Generate a strong password
DB_PASSWORD=$(openssl rand -base64 24)
echo "Database Password: $DB_PASSWORD"
# SAVE THIS PASSWORD - you'll need it later!
```

### Step 3: Deploy Infrastructure with Bicep

```bash
# Deploy using Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infra/main.bicep \
  --parameters \
    applicationName=patchhive \
    environmentName=$ENVIRONMENT \
    location=$LOCATION \
    databaseAdminUsername=patchhive \
    databaseAdminPassword="$DB_PASSWORD" \
    appServiceSku=B1 \
    postgresSku=Standard_B1ms
```

**Deployment takes ~8-12 minutes.** You'll see outputs when complete:

```json
{
  "backendUrl": "https://patchhive-dev-api.azurewebsites.net",
  "databaseHost": "patchhive-dev-db.postgres.database.azure.com",
  "databaseName": "patchhive",
  "frontendUrl": "https://patchhive-dev-web.azurestaticapps.net",
  "resourceGroupName": "patchhive-rg"
}
```

### Step 4: Deploy Backend Code

```bash
# Navigate to backend directory
cd backend

# Create deployment package
zip -r ../backend.zip . -x "*.pyc" -x "__pycache__/*" -x ".env"

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --src ../backend.zip

# Stream logs to verify deployment
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api
```

Look for:
```
Starting PatchHive v0.1.0
ABX-Core version: 1.2
```

### Step 5: Deploy Frontend Code

#### Option A: GitHub Integration (Recommended)

```bash
# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP \
  --query "properties.apiKey" -o tsv)

# Configure as GitHub secret
echo "Add this token to GitHub Secrets as AZURE_STATIC_WEB_APPS_API_TOKEN"
echo $DEPLOYMENT_TOKEN
```

Then create `.github/workflows/azure-static-web-apps.yml`:

```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build And Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "frontend"
          output_location: "dist"
```

#### Option B: Manual Build and Deploy

```bash
cd frontend

# Build
npm install
npm run build

# Deploy
az staticwebapp upload \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP \
  --source-path ./dist
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (App Service Settings)

Configure via Azure Portal or CLI:

```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --settings \
    DATABASE_URL="postgresql://patchhive:$DB_PASSWORD@patchhive-$ENVIRONMENT-db.postgres.database.azure.com/patchhive" \
    SECRET_KEY="your-secret-key-generate-with-openssl" \
    CORS_ORIGINS="https://patchhive-$ENVIRONMENT-web.azurestaticapps.net" \
    APP_NAME="PatchHive" \
    APP_VERSION="1.0.0" \
    ABX_CORE_VERSION="1.2" \
    ENFORCE_SEED_TRACEABILITY="true"
```

#### Frontend (Static Web App Settings)

```bash
az staticwebapp appsettings set \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP \
  --setting-names \
    VITE_API_URL="https://patchhive-$ENVIRONMENT-api.azurewebsites.net"
```

### Database Configuration

#### Enable SSL Connections (Recommended)

```bash
az postgres flexible-server parameter set \
  --resource-group $RESOURCE_GROUP \
  --server-name patchhive-$ENVIRONMENT-db \
  --name require_secure_transport \
  --value on
```

Update DATABASE_URL to use SSL:
```
postgresql://patchhive:password@host.postgres.database.azure.com/patchhive?sslmode=require
```

#### Configure Firewall Rules

```bash
# Allow your IP for database management
MY_IP=$(curl -s ifconfig.me)
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-db \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP

# Azure services are already allowed by the template
```

---

## 🧪 Post-Deployment

### 1. Verify Deployment

```bash
# Get the URLs
BACKEND_URL=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.backendUrl.value -o tsv)

FRONTEND_URL=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.frontendUrl.value -o tsv)

echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
```

### 2. Test Backend API

```bash
# Health check
curl $BACKEND_URL/health
# Expected: {"status":"healthy"}

# API root
curl $BACKEND_URL/
# Expected: {"message":"Welcome to PatchHive API"}

# List modules (initially empty)
curl $BACKEND_URL/modules
# Expected: []
```

### 3. Test Frontend

```bash
# Check frontend is accessible
curl -I $FRONTEND_URL
# Expected: HTTP/1.1 200 OK
```

Visit the frontend URL in your browser to verify the UI loads.

### 4. Test Database Connection

```bash
# Connect to database
psql "postgresql://patchhive:$DB_PASSWORD@patchhive-$ENVIRONMENT-db.postgres.database.azure.com/patchhive?sslmode=require"

# List tables (created automatically on first backend startup)
\dt

# Expected tables:
# - modules
# - cases
# - racks
# - rack_modules
# - patches
# - users
# - votes
# - comments
```

### 5. Monitor Application

```bash
# View backend logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api

# View deployment logs
az webapp log deployment show \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api
```

---

## 🔍 Troubleshooting

### Backend Issues

#### Issue: Backend shows "Application Error"

**Check logs:**
```bash
az webapp log tail --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api
```

**Common causes:**
1. Missing environment variables
2. Database connection failure
3. Python dependency installation failure

**Fix:**
```bash
# Restart the app
az webapp restart --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api

# Verify environment variables
az webapp config appsettings list --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api
```

#### Issue: Database tables not created

**Solution:**
```bash
# SSH into the app service
az webapp ssh --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api

# Run database initialization manually
cd backend
python3 -c "from core.database import init_db; init_db()"
```

### Frontend Issues

#### Issue: Frontend shows blank page

**Check browser console for API connection errors.**

**Fix CORS:**
```bash
# Update CORS_ORIGINS to include frontend URL
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --settings CORS_ORIGINS="https://patchhive-$ENVIRONMENT-web.azurestaticapps.net"
```

#### Issue: Frontend can't connect to backend

**Verify VITE_API_URL:**
```bash
az staticwebapp appsettings list \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP
```

**Update if needed:**
```bash
az staticwebapp appsettings set \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP \
  --setting-names VITE_API_URL="https://patchhive-$ENVIRONMENT-api.azurewebsites.net"
```

### Database Issues

#### Issue: Can't connect to database

**Check firewall rules:**
```bash
az postgres flexible-server firewall-rule list \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-db
```

**Test connection:**
```bash
psql "postgresql://patchhive:$DB_PASSWORD@patchhive-$ENVIRONMENT-db.postgres.database.azure.com/patchhive?sslmode=require"
```

---

## 💰 Cost Estimation

### Monthly Cost Breakdown (USD)

| Resource | Tier | Estimated Cost |
|----------|------|----------------|
| **Static Web App** | Free | $0.00 |
| **App Service Plan (B1)** | 1 instance | ~$13.00 |
| **PostgreSQL Flexible Server (B1ms)** | Burstable | ~$12.00 |
| **Bandwidth** | First 5GB free | ~$0.00 - $5.00 |
| **Storage** | 32 GB database | Included |
| **Total** | | **~$25.00 - $30.00/month** |

### Cost Optimization Tips

1. **Use Free Tier for Development:**
   - Azure Free Account includes $200 credit
   - Free tier Static Web Apps (forever free)

2. **Scale Down for Testing:**
   ```bash
   # Use F1 (Free) tier for App Service during development
   az appservice plan update \
     --resource-group $RESOURCE_GROUP \
     --name patchhive-$ENVIRONMENT-plan \
     --sku F1
   ```

3. **Auto-Shutdown for Dev Environments:**
   ```bash
   # Stop App Service when not in use
   az webapp stop --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api

   # Start when needed
   az webapp start --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api
   ```

4. **Database Auto-Pause (if available for your tier):**
   Configure auto-pause for non-production databases

---

## 🔒 Security Best Practices

### 1. Use Azure Key Vault for Secrets

```bash
# Create Key Vault
az keyvault create \
  --name patchhive-$ENVIRONMENT-kv \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store database password
az keyvault secret set \
  --vault-name patchhive-$ENVIRONMENT-kv \
  --name database-password \
  --value "$DB_PASSWORD"

# Grant App Service access
az webapp identity assign \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api

# Reference secret in app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --settings DATABASE_PASSWORD="@Microsoft.KeyVault(SecretUri=https://patchhive-$ENVIRONMENT-kv.vault.azure.net/secrets/database-password/)"
```

### 2. Enable HTTPS Only

```bash
az webapp update \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --set httpsOnly=true
```

### 3. Configure Custom Domain with SSL

```bash
# Add custom domain
az staticwebapp hostname set \
  --name patchhive-$ENVIRONMENT-web \
  --resource-group $RESOURCE_GROUP \
  --hostname patchhive.yourdomain.com

# SSL is automatically configured
```

### 4. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app patchhive-$ENVIRONMENT-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Link to App Service
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app patchhive-$ENVIRONMENT-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name patchhive-$ENVIRONMENT-api \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

---

## 📚 Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Static Web Apps Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure PostgreSQL Flexible Server Documentation](https://docs.microsoft.com/en-us/azure/postgresql/flexible-server/)
- [Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)

---

## 🆘 Support

### Issue: Need help with deployment?

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review Azure deployment logs
3. Open an issue on [GitHub](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues)

### Cleanup Resources

To delete all Azure resources:

```bash
# Delete entire resource group (WARNING: This deletes everything!)
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait
```

---

**Status: Ready for Azure deployment** ✅
