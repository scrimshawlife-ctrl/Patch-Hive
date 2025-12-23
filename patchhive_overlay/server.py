"""
Patch-Hive Abraxas Overlay HTTP Server

Exposes Patch-Hive as an AAL-core overlay service with:
- Stable HTTP interface: /health, /run
- Deterministic JSON + provenance tracking
- Thin HTTP adapter mode: calls existing Patch-Hive backend

Usage:
    python -m patchhive_overlay.server --host 127.0.0.1 --port 8791 --backend-base http://127.0.0.1:8000

Capabilities:
    - patchhive.ping            Check overlay + backend health
    - patchhive.echo            Echo input payload
    - patchhive.generate_patch  Generate patch suggestions
    - patchhive.search          Search module catalog
"""
from __future__ import annotations

import argparse
import json
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .provenance import make_provenance

JSON_CT = "application/json; charset=utf-8"


# ============================================================
# Backend HTTP adapter (stdlib only)
# ============================================================
def _canon_json_bytes(obj: Dict[str, Any]) -> bytes:
    """Serialize dict to canonical JSON bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _http_get_json(url: str, timeout_s: int) -> Dict[str, Any]:
    """HTTP GET request expecting JSON response."""
    req = Request(url=url, method="GET")
    with urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
        out = json.loads(raw) if raw else {}
        if not isinstance(out, dict):
            return {"raw": raw}
        return out


def _http_post_json(url: str, body: Dict[str, Any], timeout_s: int) -> Dict[str, Any]:
    """HTTP POST request with JSON body, expecting JSON response."""
    raw = _canon_json_bytes(body)
    req = Request(url=url, data=raw, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout_s) as resp:
        data = resp.read().decode("utf-8")
        out = json.loads(data) if data else {}
        if not isinstance(out, dict):
            raise ValueError("backend returned non-object JSON")
        return out


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    """Read JSON request body from HTTP handler."""
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("root must be object")
    return obj


def _write_json(handler: BaseHTTPRequestHandler, status: int, body: Dict[str, Any]) -> None:
    """Write JSON response to HTTP handler."""
    raw = _canon_json_bytes(body)
    handler.send_response(status)
    handler.send_header("Content-Type", JSON_CT)
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


# ============================================================
# Capability Router
# ============================================================
def _capability_router(cap: str, payload: Dict[str, Any], backend_base: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Route capability requests to appropriate backend endpoints.

    Supported capabilities:
      - patchhive.ping            -> GET {backend_base}/health
      - patchhive.echo            -> Local echo (no backend call)
      - patchhive.generate_patch  -> POST {backend_base}/api/patches/generate
      - patchhive.search          -> GET {backend_base}/api/modules/catalog

    Args:
        cap: Capability name (e.g., "patchhive.generate_patch")
        payload: Input payload for the capability
        backend_base: Base URL of Patch-Hive backend

    Returns:
        Tuple of (success: bool, result: dict)
    """
    if cap == "patchhive.echo":
        return True, {"echo": payload}

    if cap == "patchhive.ping":
        # Try hitting backend health; if it fails, still return overlay OK but mark backend unreachable.
        backend_health_url = f"{backend_base}/health"
        try:
            bh = _http_get_json(backend_health_url, timeout_s=5)
            return True, {"pong": True, "backend_base": backend_base, "backend_health": bh}
        except Exception as e:
            return True, {"pong": True, "backend_base": backend_base, "backend_health": None, "backend_error": str(e)}

    if cap == "patchhive.generate_patch":
        # Expected payload: rack_id, max_patches, seed, etc.
        # Route to Patch-Hive's patch generation endpoint
        try:
            out = _http_post_json(f"{backend_base}/api/patches/generate", payload, timeout_s=20)
            return True, {"backend": out}
        except HTTPError as e:
            return False, {"message": "backend HTTP error", "status": getattr(e, "code", None), "error": str(e)}
        except URLError as e:
            return False, {"message": "backend unreachable", "error": str(e), "backend_base": backend_base}
        except Exception as e:
            return False, {"message": "backend call failed", "error": str(e)}

    if cap == "patchhive.search":
        # Expected payload: search, brand, category, hp_min, hp_max, etc.
        # Route to Patch-Hive's catalog search endpoint
        try:
            # Build query string from payload
            params = []
            for k, v in payload.items():
                if v is not None:
                    params.append(f"{k}={v}")
            query_string = "&".join(params) if params else ""
            url = f"{backend_base}/api/modules/catalog"
            if query_string:
                url += f"?{query_string}"

            out = _http_get_json(url, timeout_s=15)
            return True, {"backend": out}
        except HTTPError as e:
            return False, {"message": "backend HTTP error", "status": getattr(e, "code", None), "error": str(e)}
        except URLError as e:
            return False, {"message": "backend unreachable", "error": str(e), "backend_base": backend_base}
        except Exception as e:
            return False, {"message": "backend call failed", "error": str(e)}

    return False, {
        "message": f"unknown capability: {cap}",
        "known": ["patchhive.ping", "patchhive.echo", "patchhive.generate_patch", "patchhive.search"],
        "note": "If your backend routes differ, edit the endpoints in _capability_router()."
    }


# ============================================================
# HTTP Server
# ============================================================
class PatchHiveOverlayHandler(BaseHTTPRequestHandler):
    """HTTP handler for Patch-Hive overlay service."""

    server_version = "patchhive-overlay/0.1"

    # Default backend base URL (overridden by server arg)
    backend_base_default: str = "http://127.0.0.1:8000"

    def log_message(self, fmt: str, *args: Any) -> None:
        """Suppress default HTTP logging."""
        return

    def do_GET(self) -> None:
        """Handle GET requests (health check only)."""
        if self.path == "/health":
            _write_json(self, 200, {"ok": True, "service": "patchhive_overlay", "version": "0.1"})
            return
        _write_json(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        """Handle POST requests (capability invocation)."""
        if self.path != "/run":
            _write_json(self, 404, {"ok": False, "error": "not found"})
            return

        try:
            req = _read_json(self)
        except Exception as e:
            _write_json(self, 400, {"ok": False, "error": f"invalid json: {e}"})
            return

        cap = req.get("capability", "patchhive.echo")
        seed = req.get("seed")
        input_payload = req.get("input", {})
        backend_base = req.get("backend_base", self.backend_base_default)

        if not isinstance(input_payload, dict):
            _write_json(self, 400, {"ok": False, "error": "input must be an object"})
            return
        if not isinstance(backend_base, str) or not backend_base.startswith(("http://", "https://")):
            _write_json(self, 400, {"ok": False, "error": "backend_base must be http(s) URL"})
            return

        prov = make_provenance("patchhive", cap, input_payload, seed=seed).to_dict()
        ok, out = _capability_router(cap, input_payload, backend_base)

        if ok:
            _write_json(self, 200, {"ok": True, "result": out, "error": None, "provenance": prov})
        else:
            _write_json(self, 200, {"ok": False, "result": None, "error": out, "provenance": prov})


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for concurrent request handling."""
    daemon_threads = True


def main() -> None:
    """Main entry point for overlay server."""
    ap = argparse.ArgumentParser(description="Patch-Hive Abraxas Overlay Server")
    ap.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    ap.add_argument("--port", type=int, default=8791, help="Port to listen on (default: 8791)")
    ap.add_argument("--backend-base", default="http://127.0.0.1:8000",
                    help="Patch-Hive backend base URL (default: http://127.0.0.1:8000)")
    args = ap.parse_args()

    # Inject backend base into handler class
    PatchHiveOverlayHandler.backend_base_default = args.backend_base

    print(f"Starting Patch-Hive Overlay Server...")
    print(f"  Listening on: http://{args.host}:{args.port}")
    print(f"  Backend base: {args.backend_base}")
    print(f"  Endpoints:")
    print(f"    GET  /health - Health check")
    print(f"    POST /run    - Capability invocation")
    print()

    srv = ThreadedHTTPServer((args.host, args.port), PatchHiveOverlayHandler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down overlay server...")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
