from fastapi import FastAPI

app = FastAPI(title="Misis API", version="1.0.1")


@app.get("/hello")
async def hello_misis():
    return {"message": "hello misis"}
