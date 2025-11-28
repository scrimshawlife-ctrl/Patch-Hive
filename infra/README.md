# Infrastructure as Code

This directory contains Infrastructure as Code (IaC) templates for deploying PatchHive to various cloud platforms.

## 📁 Directory Structure

```
infra/
├── main.bicep                 # Azure Bicep template (main infrastructure)
├── main.parameters.json       # Azure deployment parameters
└── README.md                  # This file
```

## 🌩️ Azure Deployment

### Quick Start

```bash
# Deploy with Azure Developer CLI (recommended)
azd up

# Or deploy with Azure CLI
az deployment group create \
  --resource-group patchhive-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

### What Gets Created

The Bicep template (`main.bicep`) creates:

1. **Azure PostgreSQL Flexible Server**
   - PostgreSQL 15
   - Burstable B1ms tier (2 vCores, 2 GB RAM)
   - 32 GB storage
   - 7-day backup retention
   - Firewall rules for Azure services

2. **Azure App Service Plan**
   - Linux-based plan
   - B1 tier (1.75 GB RAM)
   - Reserved for Python runtime

3. **Azure App Service (Backend)**
   - Python 3.11 runtime
   - FastAPI application
   - Health check endpoint configured
   - Environment variables auto-configured
   - HTTPS enforced

4. **Azure Static Web App (Frontend)**
   - Free tier
   - React/Vite application
   - Automatic builds from GitHub
   - Custom domain support
   - Automatic SSL

### Resource Naming Convention

All resources follow the pattern: `{applicationName}-{environmentName}-{resourceType}`

Examples:
- `patchhive-dev-db` - Development database
- `patchhive-prod-api` - Production backend API
- `patchhive-staging-web` - Staging frontend

### Parameters

Edit `main.parameters.json` to customize:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `applicationName` | Prefix for all resources | `patchhive` |
| `environmentName` | Environment (dev/staging/prod) | `dev` |
| `location` | Azure region | Resource group location |
| `databaseAdminUsername` | PostgreSQL admin username | `patchhive` |
| `databaseAdminPassword` | PostgreSQL admin password | *Required* |
| `appServiceSku` | App Service tier | `B1` |
| `postgresSku` | PostgreSQL tier | `Standard_B1ms` |

### Outputs

After deployment, the template provides:

```json
{
  "databaseHost": "patchhive-dev-db.postgres.database.azure.com",
  "databaseName": "patchhive",
  "backendUrl": "https://patchhive-dev-api.azurewebsites.net",
  "frontendUrl": "https://patchhive-dev-web.azurestaticapps.net",
  "resourceGroupName": "patchhive-rg"
}
```

## 🛠️ Local Development with Azure Resources

### Connect to Azure PostgreSQL Locally

```bash
# Get database connection string
az postgres flexible-server show-connection-string \
  --server-name patchhive-dev-db \
  --database-name patchhive \
  --admin-user patchhive \
  --admin-password $DB_PASSWORD

# Connect with psql
psql "postgresql://patchhive:PASSWORD@patchhive-dev-db.postgres.database.azure.com/patchhive?sslmode=require"
```

### Test Backend API Locally with Azure Database

```bash
cd backend

# Set environment variables
export DATABASE_URL="postgresql://patchhive:PASSWORD@patchhive-dev-db.postgres.database.azure.com/patchhive?sslmode=require"
export SECRET_KEY="dev-secret-key"
export CORS_ORIGINS="http://localhost:5173"

# Run locally
uvicorn main:app --reload
```

## 📊 Cost Management

### Development Environment

Recommended tiers for development:

```bicep
param appServiceSku = 'F1'        // Free tier (limited)
param postgresSku = 'Standard_B1ms'  // ~$12/month
```

**Estimated cost:** ~$12-15/month

### Production Environment

Recommended tiers for production:

```bicep
param appServiceSku = 'B2'        // ~$55/month
param postgresSku = 'Standard_B2s'  // ~$30/month
```

**Estimated cost:** ~$85-100/month

### Cost Optimization Tips

1. **Stop/Start App Services** when not in use:
   ```bash
   az webapp stop --name patchhive-dev-api --resource-group patchhive-rg
   az webapp start --name patchhive-dev-api --resource-group patchhive-rg
   ```

2. **Use Azure Reservations** for 1-3 year commitments (up to 72% savings)

3. **Set up Azure Budgets** to monitor spending:
   ```bash
   az consumption budget create \
     --budget-name patchhive-budget \
     --amount 50 \
     --time-grain Monthly \
     --resource-group patchhive-rg
   ```

## 🔒 Security Best Practices

### 1. Store Secrets in Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name patchhive-dev-kv \
  --resource-group patchhive-rg

# Store database password
az keyvault secret set \
  --vault-name patchhive-dev-kv \
  --name database-password \
  --value "$DB_PASSWORD"

# Reference in Bicep:
# @secure()
# param databasePassword string = az.keyVault('patchhive-dev-kv').getSecret('database-password')
```

### 2. Enable Private Endpoints (Production)

For production, consider using Azure Private Link to secure database connections.

### 3. Configure Network Security

Update `main.bicep` to restrict IP access:

```bicep
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowSpecificIP'
  properties: {
    startIpAddress: 'YOUR_IP'
    endIpAddress: 'YOUR_IP'
  }
}
```

## 🚀 CI/CD Integration

### GitHub Actions

The repository includes `.github/workflows/azure-deploy.yml` for automated deployments.

**Setup:**

1. Create Azure Service Principal:
   ```bash
   az ad sp create-for-rbac \
     --name patchhive-github \
     --role contributor \
     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/patchhive-rg \
     --sdk-auth
   ```

2. Add GitHub Secrets:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `DB_ADMIN_PASSWORD`

3. Trigger deployment:
   ```bash
   # Manual trigger via GitHub UI: Actions > Deploy to Azure > Run workflow
   ```

## 🧹 Cleanup

### Delete All Resources

```bash
# WARNING: This deletes everything!
az group delete \
  --name patchhive-rg \
  --yes \
  --no-wait
```

### Delete Specific Resources

```bash
# Delete only the backend
az webapp delete \
  --name patchhive-dev-api \
  --resource-group patchhive-rg

# Delete only the database
az postgres flexible-server delete \
  --name patchhive-dev-db \
  --resource-group patchhive-rg
```

## 📚 Additional Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure PostgreSQL Flexible Server](https://docs.microsoft.com/en-us/azure/postgresql/flexible-server/)
- [Azure Static Web Apps](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)

## 🆘 Troubleshooting

### Issue: Bicep deployment fails

**Check deployment logs:**
```bash
az deployment group show \
  --resource-group patchhive-rg \
  --name main \
  --query properties.error
```

### Issue: Database connection fails

**Verify firewall rules:**
```bash
az postgres flexible-server firewall-rule list \
  --resource-group patchhive-rg \
  --name patchhive-dev-db
```

### Issue: Backend shows 500 errors

**Check App Service logs:**
```bash
az webapp log tail \
  --resource-group patchhive-rg \
  --name patchhive-dev-api
```

---

For detailed deployment instructions, see [AZURE_DEPLOYMENT.md](../docs/AZURE_DEPLOYMENT.md)
