#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║         PatchHive Backend - Replit Setup               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e . --quiet

# Create export directory
echo "📁 Creating export directory..."
mkdir -p /tmp/exports

# Environment check
echo "🔧 Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
  echo "⚠️  WARNING: DATABASE_URL not set!"
  echo "   Set it in Replit Secrets or .env file"
  echo "   Example: postgresql://user:pass@host:5432/patchhive"
else
  echo "✅ DATABASE_URL configured"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 To run the backend:"
echo "   uvicorn main:app --host 0.0.0.0 --port 3000"
echo ""
echo "🧪 To run tests:"
echo "   pytest -v tests/unit/test_patchbook_unit.py"
echo "   pytest -v tests/api/test_export_api.py"
echo ""
