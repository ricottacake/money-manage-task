import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "backend:create_app",
        host="0.0.0.0",
        port=8040,
        reload=True
    )
