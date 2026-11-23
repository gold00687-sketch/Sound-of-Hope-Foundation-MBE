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

    if not settings.is_production:
        print("\n" + "=" * 50)
        print(f"  Swagger docs:  http://localhost:8000/docs")
        print(f"  ReDoc docs:    http://localhost:8000/redoc")
        print("=" * 50 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="debug" if settings.app_debug else "info",
    )
