from fastapi import FastAPI

app = FastAPI(title="Sales Management API")

@app.get("/")
def root():
    return {"message": "Backend is running"}

