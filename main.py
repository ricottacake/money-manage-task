

if __name__ == "__main__":
    import sys
    from pathlib import Path

    import uvicorn

    sys.path.append(str(Path(__file__).parent))

    uvicorn.run(
        "app:create_app",
        host="0.0.0.0",
        port= 80,
        reload=True
    )
