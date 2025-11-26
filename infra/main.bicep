// Azure Infrastructure for PatchHive
// Deploys: PostgreSQL Flexible Server, App Service, Static Web App

targetScope = 'resourceGroup'

@description('Name of the application (used as prefix for resources)')
param applicationName string = 'patchhive'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('Database administrator username')
@secure()
param databaseAdminUsername string = 'patchhive'

@description('Database administrator password')
@secure()
param databaseAdminPassword string

@description('App Service SKU')
param appServiceSku string = 'B1'

@description('PostgreSQL SKU')
param postgresSku string = 'Standard_B1ms'

// Variables
var resourcePrefix = '${applicationName}-${environmentName}'
var databaseName = 'patchhive'

// PostgreSQL Flexible Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: '${resourcePrefix}-db'
  location: location
  sku: {
    name: postgresSku
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: databaseAdminUsername
    administratorLoginPassword: databaseAdminPassword
    version: '15'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// PostgreSQL Firewall Rule - Allow Azure Services
resource firewallRuleAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// App Service Plan for Backend
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${resourcePrefix}-plan'
  location: location
  sku: {
    name: appServiceSku
  }
  properties: {
    reserved: true // Required for Linux
  }
  kind: 'linux'
}

// App Service for Backend API
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${resourcePrefix}-api'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'cd backend && uvicorn main:app --host 0.0.0.0 --port 8000'
      healthCheckPath: '/health'
      alwaysOn: false
      appSettings: [
        {
          name: 'DATABASE_URL'
          value: 'postgresql://${databaseAdminUsername}:${databaseAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}/${databaseName}'
        }
        {
          name: 'SECRET_KEY'
          value: uniqueString(resourceGroup().id, applicationName)
        }
        {
          name: 'CORS_ORIGINS'
          value: 'https://${staticWebApp.properties.defaultHostname}'
        }
        {
          name: 'APP_NAME'
          value: 'PatchHive'
        }
        {
          name: 'APP_VERSION'
          value: '1.0.0'
        }
        {
          name: 'ABX_CORE_VERSION'
          value: '1.2'
        }
        {
          name: 'ENFORCE_SEED_TRACEABILITY'
          value: 'true'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'WEBSITE_HTTPLOGGING_RETENTION_DAYS'
          value: '7'
        }
      ]
    }
    httpsOnly: true
  }
}

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: '${resourcePrefix}-web'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/scrimshawlife-ctrl/Patch-Hive'
    branch: 'main'
    buildProperties: {
      appLocation: 'frontend'
      apiLocation: ''
      outputLocation: 'dist'
    }
  }
}

// Static Web App Settings
resource staticWebAppSettings 'Microsoft.Web/staticSites/config@2023-01-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    VITE_API_URL: 'https://${appService.properties.defaultHostName}'
  }
}

// Outputs
output databaseHost string = postgresServer.properties.fullyQualifiedDomainName
output databaseName string = databaseName
output backendUrl string = 'https://${appService.properties.defaultHostName}'
output frontendUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output resourceGroupName string = resourceGroup().name
