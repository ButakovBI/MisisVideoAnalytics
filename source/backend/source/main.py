from fastapi import FastAPI


app = FastAPI(title="Backend Service", version="1.0.0")


@app.get("/hello")
async def hello_misis():
    return {"message": "hello misis"}
