from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🧠 Orchestrator is alive"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)