# 🐝 PatchHive - Replit Deployment Guide

Welcome to **PatchHive** on Replit! This guide will help you get your Eurorack system design and patch exploration platform up and running.

## 🚀 Quick Start

### Option 1: Import from ZIP (Recommended)

1. **Upload the ZIP file to Replit:**
   - Go to [Replit](https://replit.com)
   - Click "Create Repl"
   - Select "Import from GitHub" or "Upload ZIP"
   - Upload the `patchhive-replit.zip` file

2. **Run the application:**
   - Click the "Run" button at the top
   - Wait for the setup to complete (first run takes 2-3 minutes)
   - Your application will be available in the Replit webview

3. **Access your app:**
   - Frontend: Automatically displayed in webview
   - Backend API: `https://[your-repl-name].[your-username].repl.co/docs`

### Option 2: Import from GitHub

1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Enter: `https://github.com/scrimshawlife-ctrl/Patch-Hive`
5. Click "Import from GitHub"
6. Follow steps 2-3 from Option 1

## 📋 What's Included

This Replit export includes everything you need:

- ✅ Complete backend (Python/FastAPI)
- ✅ Complete frontend (React/TypeScript)
- ✅ PostgreSQL database setup
- ✅ Auto-configuration scripts
- ✅ Sample data seeding
- ✅ All dependencies

## 🎛️ Features Available

### Core Features

- **Module & Case Library** - Browse and manage Eurorack modules
- **Rack Builder** - Design your modular synthesizer systems
- **Patch Generation** - Generate deterministic patches from your racks
- **Export System** - Export patches as JSON, SVG, or PDF (Patch Book)
- **Community Features** - Share and discover racks and patches

### Key Endpoints

Once running, you can access:

| Endpoint | Description |
|----------|-------------|
| `/` | Frontend UI |
| `/docs` | Interactive API documentation (Swagger) |
| `/health` | Health check endpoint |
| `/api/modules` | Module catalog |
| `/api/racks` | Rack management |
| `/api/patches` | Patch operations |

## 🔧 Configuration

### Environment Variables

The startup script automatically configures:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT authentication secret
- `CORS_ORIGINS` - Allowed origins for API access
- `VITE_API_BASE_URL` - Frontend API endpoint

### Custom Configuration

To customize, you can set these in Replit's "Secrets" panel:

```bash
# Backend secrets
SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=["https://your-domain.com"]

# Database (auto-configured)
DATABASE_URL=postgresql://user@localhost:5432/patchhive
```

## 📁 Project Structure

```
patchhive/
├── backend/                 # FastAPI backend
│   ├── main.py             # API entry point
│   ├── alembic/            # Database migrations
│   ├── modules/            # Module catalog
│   ├── racks/              # Rack builder
│   ├── patches/            # Patch engine
│   ├── export/             # PDF/SVG export
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Build configuration
│
├── .replit                # Replit configuration
├── replit.nix             # Nix package dependencies
├── start.sh               # Startup script
└── README_REPLIT.md       # This file
```

## 🐛 Troubleshooting

### Application won't start

**Problem:** Startup fails with database errors

**Solution:**
```bash
# Reset PostgreSQL
rm -rf $PGDATA
# Click Run again
```

### Dependencies not installing

**Problem:** `pip install` or `npm install` fails

**Solution:**
1. Open the Shell tab in Replit
2. Run manually:
```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Port conflicts

**Problem:** "Port already in use" errors

**Solution:**
1. Stop the current run
2. Kill processes:
```bash
pkill -f uvicorn
pkill -f node
```
3. Click Run again

### Database migration errors

**Problem:** Alembic migration fails

**Solution:**
```bash
cd backend
alembic upgrade head
```

### Frontend not connecting to backend

**Problem:** API calls fail with CORS errors

**Solution:** Check that `VITE_API_BASE_URL` matches your backend URL in the Shell:
```bash
echo $VITE_API_BASE_URL
```

## 🔄 Updating the Application

To pull latest changes from GitHub:

```bash
# In Replit Shell
git pull origin main

# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Run migrations
cd ../backend && alembic upgrade head
```

## 💾 Database Management

### Backup Database

```bash
pg_dump -h localhost -U $USER patchhive > backup.sql
```

### Restore Database

```bash
psql -h localhost -U $USER patchhive < backup.sql
```

### Reset Database

```bash
cd backend
alembic downgrade base
alembic upgrade head
python seed_data.py
```

## 📊 Monitoring

### View Logs

Backend logs:
```bash
tail -f /tmp/backend.log
```

PostgreSQL logs:
```bash
tail -f $PGDATA/logfile
```

### Check Service Status

```bash
# Backend
curl http://localhost:8000/health

# Database
pg_isready -h localhost -p 5432
```

## 🎨 Development Tips

### Making Code Changes

1. Edit files in the Replit editor
2. Backend auto-reloads with `--reload` flag
3. Frontend hot-reloads automatically
4. Changes appear immediately

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend lint:
```bash
cd frontend
npm run lint
```

### Adding Modules

1. Go to `/api/modules` in the API docs
2. Use the POST endpoint to add modules
3. Or import from CSV via the UI

## 🌐 Making Your Repl Public

1. Click "Share" in top-right corner
2. Toggle "Public" to make it visible
3. Share your Repl URL with others
4. Users can fork and customize their own version

## 🔐 Security Notes

For production use:

1. **Change SECRET_KEY:** Set a strong random key in Secrets
2. **Update CORS_ORIGINS:** Limit to your specific domain
3. **Enable authentication:** Configure user registration limits
4. **Database backups:** Regularly backup your data
5. **Monitor usage:** Check for unusual activity

## 📚 Additional Resources

- [Main README](README.md) - Full project documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture Guide](docs/ARCHITECTURE.md) - System design
- [Patch Engine Details](docs/PATCH_ENGINE.md) - How patch generation works

## 🤝 Support & Contributing

- **Issues:** Report bugs at [GitHub Issues](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues)
- **Discussions:** Join community discussions
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🎯 Next Steps

1. ✅ Click "Run" to start your application
2. ✅ Explore the UI and create your first rack
3. ✅ Generate patches and export them
4. ✅ Share your creations with the community

**Happy patching! 🎛️✨**

---

<div align="center">

Built with ABX-Core v1.2 | SEED-Enforced | Deterministic | Modular

</div>
