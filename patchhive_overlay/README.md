# Patch-Hive Abraxas Overlay

Exposes Patch-Hive as an AAL-core overlay service with stable HTTP interface, deterministic JSON, and complete provenance tracking.

## Architecture

The overlay acts as a **thin HTTP adapter** that:
- Provides standardized `/health` and `/run` endpoints
- Wraps Patch-Hive backend calls with provenance metadata
- Enables integration with the Abraxas/AAL ecosystem
- Maintains deterministic, traceable operations

**Does NOT replace** the existing Patch-Hive backend - it sits alongside it as a translation layer.

## Quick Start

### 1. Start Patch-Hive Backend

```bash
cd backend
export DATABASE_URL="sqlite:///./patchhive.db"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Start Overlay Server

```bash
# From repository root
python -m patchhive_overlay.server \
  --host 127.0.0.1 \
  --port 8791 \
  --backend-base http://127.0.0.1:8000
```

### 3. Test Overlay

```bash
# Health check
curl http://127.0.0.1:8791/health

# Echo test
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{"capability": "patchhive.echo", "input": {"test": "hello"}}'

# Ping backend
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{"capability": "patchhive.ping"}'
```

## Capabilities

### patchhive.ping

Check overlay and backend health.

```bash
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "patchhive.ping"
  }'
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "pong": true,
    "backend_base": "http://127.0.0.1:8000",
    "backend_health": {
      "status": "healthy",
      "app": "PatchHive",
      "version": "0.1.0",
      "abx_core_version": "1.3"
    }
  },
  "provenance": {
    "run_id": "8a4dbe9e98aa...",
    "ts_utc": "2025-12-14T03:28:07+00:00",
    "payload_hash": "44136fa355b3...",
    "env": {
      "python": "3.11.14",
      "platform": "Linux-4.4.0-x86_64",
      "git_head": "18c50a9f50931...",
      "cwd": "/home/user/Patch-Hive"
    }
  }
}
```

### patchhive.echo

Echo input payload (for testing).

```bash
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "patchhive.echo",
    "input": {"message": "hello world"}
  }'
```

### patchhive.search

Search module catalog.

```bash
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "patchhive.search",
    "input": {
      "search": "maths",
      "category": "ENV",
      "limit": 10
    }
  }'
```

**Backend Route:** `GET /api/modules/catalog?search=maths&category=ENV&limit=10`

### patchhive.generate_patch

Generate patch suggestions for a rack.

```bash
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "patchhive.generate_patch",
    "input": {
      "rack_id": 1,
      "max_patches": 5,
      "seed": "deterministic-seed"
    },
    "seed": "deterministic-seed"
  }'
```

**Backend Route:** `POST /api/patches/generate`

## Provenance

Every `/run` invocation includes complete provenance:

- **run_id**: Deterministic SHA-256 hash based on:
  - Overlay name ("patchhive")
  - Capability name
  - Input payload hash
  - Seed (or timestamp if no seed provided)

- **ts_utc**: ISO 8601 UTC timestamp

- **payload_hash**: SHA-256 of canonical JSON input

- **env**: Environment fingerprint
  - Python version
  - Platform details
  - Git HEAD commit (if available)
  - Working directory

### Deterministic Run IDs

Provide a `seed` field for reproducible run IDs:

```json
{
  "capability": "patchhive.generate_patch",
  "seed": "my-deterministic-seed",
  "input": {...}
}
```

Same capability + input + seed = Same run_id

## API Reference

### GET /health

Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "service": "patchhive_overlay",
  "version": "0.1"
}
```

### POST /run

Capability invocation endpoint.

**Request Body:**
```json
{
  "capability": "patchhive.ping",
  "input": {},
  "seed": "optional-seed",
  "backend_base": "http://127.0.0.1:8000"
}
```

**Fields:**
- `capability` (string, required): Capability name (e.g., "patchhive.ping")
- `input` (object, optional): Input payload for capability (default: `{}`)
- `seed` (string, optional): Seed for deterministic run_id
- `backend_base` (string, optional): Override default backend URL

**Response (Success):**
```json
{
  "ok": true,
  "result": {...},
  "error": null,
  "provenance": {...}
}
```

**Response (Error):**
```json
{
  "ok": false,
  "result": null,
  "error": {
    "message": "error description",
    ...
  },
  "provenance": {...}
}
```

## Configuration

### Command-Line Arguments

```bash
python -m patchhive_overlay.server --help
```

- `--host`: Host to bind to (default: `127.0.0.1`)
- `--port`: Port to listen on (default: `8791`)
- `--backend-base`: Patch-Hive backend URL (default: `http://127.0.0.1:8000`)

### Environment Variables

Currently none - all configuration via CLI args.

## Integration with Abraxas

This overlay follows the AAL-core overlay specification:

1. **Stable Interface**: `/health` and `/run` endpoints
2. **Deterministic**: Same input + seed = Same output + run_id
3. **Provenance**: Complete traceability of all operations
4. **Stateless**: No session state, all context in request
5. **Standard JSON**: Canonical serialization for hashing

## Backend Route Mapping

The overlay maps capabilities to Patch-Hive backend routes:

| Capability | Method | Backend Route | Notes |
|------------|--------|---------------|-------|
| `patchhive.ping` | GET | `/health` | Health check |
| `patchhive.echo` | - | (local) | No backend call |
| `patchhive.search` | GET | `/api/modules/catalog` | Query params from input |
| `patchhive.generate_patch` | POST | `/api/patches/generate` | JSON body from input |

### Customizing Routes

Edit `_capability_router()` in `server.py` to change backend endpoints.

## Development

### Running Tests

```bash
# Test overlay endpoints
curl http://127.0.0.1:8791/health

# Test with different capabilities
curl -X POST http://127.0.0.1:8791/run \
  -H "Content-Type: application/json" \
  -d '{"capability": "patchhive.ping"}'
```

### Adding New Capabilities

1. Add capability to `_capability_router()` in `server.py`
2. Map to appropriate backend endpoint
3. Handle errors and timeouts
4. Update this documentation

## Troubleshooting

### "backend unreachable" error

- Ensure Patch-Hive backend is running on specified port
- Check `--backend-base` URL is correct
- Verify network connectivity

### "unknown capability" error

- Check capability name spelling
- See list of known capabilities in error message
- Refer to documentation above

### Provenance run_id not deterministic

- Ensure you're providing a `seed` field
- Verify input payload is identical
- Check that capability name hasn't changed

## License

Same as Patch-Hive main project.

## See Also

- [ABX-Core v1.3 Compliance](../docs/ABX_CORE_COMPLIANCE.md)
- [Catalog Architecture](../backend/CATALOG_ARCHITECTURE.md)
- [Bootstrap Documentation](../backend/integrations/README.md)
