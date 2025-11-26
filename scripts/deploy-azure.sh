#!/bin/bash
# Azure Deployment Script for PatchHive
# Deploys backend, frontend, and database to Azure

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   PatchHive Azure Deployment Script      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli${NC}"
    exit 1
fi

if ! command -v azd &> /dev/null; then
    echo -e "${YELLOW}⚠️  Azure Developer CLI not found. Install for easier deployment: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd${NC}"
    AZD_AVAILABLE=false
else
    AZD_AVAILABLE=true
fi

echo -e "${GREEN}✓ Prerequisites check complete${NC}"
echo ""

# Login check
echo -e "${YELLOW}Checking Azure authentication...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in. Opening Azure login...${NC}"
    az login
fi

ACCOUNT_NAME=$(az account show --query name -o tsv)
echo -e "${GREEN}✓ Logged in as: $ACCOUNT_NAME${NC}"
echo ""

# Deployment method selection
echo "Select deployment method:"
echo "1) Azure Developer CLI (azd up) - Recommended"
echo "2) Manual Bicep deployment"
echo "3) Exit"
read -p "Enter choice [1-3]: " CHOICE

case $CHOICE in
    1)
        if [ "$AZD_AVAILABLE" = false ]; then
            echo -e "${RED}❌ Azure Developer CLI (azd) is not installed.${NC}"
            echo "Install it from: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd"
            exit 1
        fi

        echo -e "${GREEN}Starting Azure Developer CLI deployment...${NC}"
        azd up
        ;;

    2)
        echo -e "${GREEN}Starting manual Bicep deployment...${NC}"
        echo ""

        # Get deployment parameters
        read -p "Resource Group name [patchhive-rg]: " RESOURCE_GROUP
        RESOURCE_GROUP=${RESOURCE_GROUP:-patchhive-rg}

        read -p "Azure region [eastus]: " LOCATION
        LOCATION=${LOCATION:-eastus}

        read -p "Environment [dev]: " ENVIRONMENT
        ENVIRONMENT=${ENVIRONMENT:-dev}

        read -p "App Service SKU [B1]: " APP_SKU
        APP_SKU=${APP_SKU:-B1}

        read -p "PostgreSQL SKU [Standard_B1ms]: " DB_SKU
        DB_SKU=${DB_SKU:-Standard_B1ms}

        # Generate database password
        DB_PASSWORD=$(openssl rand -base64 24)
        echo ""
        echo -e "${YELLOW}Generated database password (SAVE THIS):${NC}"
        echo -e "${GREEN}$DB_PASSWORD${NC}"
        echo ""
        read -p "Press Enter to continue..."

        # Create resource group
        echo -e "${YELLOW}Creating resource group...${NC}"
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION"
        echo -e "${GREEN}✓ Resource group created${NC}"

        # Deploy infrastructure
        echo -e "${YELLOW}Deploying infrastructure with Bicep...${NC}"
        az deployment group create \
            --resource-group "$RESOURCE_GROUP" \
            --template-file infra/main.bicep \
            --parameters \
                applicationName=patchhive \
                environmentName="$ENVIRONMENT" \
                location="$LOCATION" \
                databaseAdminUsername=patchhive \
                databaseAdminPassword="$DB_PASSWORD" \
                appServiceSku="$APP_SKU" \
                postgresSku="$DB_SKU"

        # Get outputs
        BACKEND_URL=$(az deployment group show \
            --resource-group "$RESOURCE_GROUP" \
            --name main \
            --query properties.outputs.backendUrl.value -o tsv)

        FRONTEND_URL=$(az deployment group show \
            --resource-group "$RESOURCE_GROUP" \
            --name main \
            --query properties.outputs.frontendUrl.value -o tsv)

        echo -e "${GREEN}✓ Infrastructure deployed successfully!${NC}"
        echo ""
        echo "Backend URL:  $BACKEND_URL"
        echo "Frontend URL: $FRONTEND_URL"
        echo ""

        # Deploy backend
        read -p "Deploy backend code? [Y/n]: " DEPLOY_BACKEND
        DEPLOY_BACKEND=${DEPLOY_BACKEND:-Y}

        if [[ $DEPLOY_BACKEND =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Deploying backend...${NC}"
            cd backend
            zip -r ../backend.zip . -x "*.pyc" -x "__pycache__/*" -x ".env" -x "tests/*"
            cd ..

            az webapp deployment source config-zip \
                --resource-group "$RESOURCE_GROUP" \
                --name "patchhive-$ENVIRONMENT-api" \
                --src backend.zip

            rm backend.zip
            echo -e "${GREEN}✓ Backend deployed${NC}"
        fi

        # Deploy frontend
        read -p "Deploy frontend code? [Y/n]: " DEPLOY_FRONTEND
        DEPLOY_FRONTEND=${DEPLOY_FRONTEND:-Y}

        if [[ $DEPLOY_FRONTEND =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Building and deploying frontend...${NC}"
            cd frontend
            npm install
            npm run build

            if command -v az staticwebapp &> /dev/null; then
                az staticwebapp upload \
                    --name "patchhive-$ENVIRONMENT-web" \
                    --resource-group "$RESOURCE_GROUP" \
                    --source-path ./dist
                echo -e "${GREEN}✓ Frontend deployed${NC}"
            else
                echo -e "${YELLOW}⚠️  Static Web App CLI not available. Please deploy via GitHub Actions or Azure Portal.${NC}"
                echo "See: docs/AZURE_DEPLOYMENT.md for instructions"
            fi
            cd ..
        fi

        echo ""
        echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║         Deployment Complete! 🎉           ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
        echo ""
        echo "Backend:  $BACKEND_URL"
        echo "Frontend: $FRONTEND_URL"
        echo ""
        echo "Next steps:"
        echo "1. Test backend: curl $BACKEND_URL/health"
        echo "2. Visit frontend: $FRONTEND_URL"
        echo "3. Review logs: az webapp log tail --resource-group $RESOURCE_GROUP --name patchhive-$ENVIRONMENT-api"
        ;;

    3)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
