import os
import sys
import traceback

try:
    import uvicorn
    from app.core.config import get_settings
except Exception as exc:
    print(f"[run.py] Failed to import dependencies: {exc}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    try:
        settings = get_settings()
    except Exception as exc:
        print(f"[run.py] Configuration error: {exc}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # Railway (and other PaaS) inject $PORT; fall back to 8000 for local dev.
    port = int(os.environ.get("PORT", 8000))

    if not settings.is_production:
        print("\n" + "=" * 50)
        print(f"  Swagger docs:  http://localhost:{port}/docs")
        print(f"  ReDoc docs:    http://localhost:{port}/redoc")
        print("=" * 50 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.is_development,
        log_level="debug" if settings.app_debug else "info",
    )
