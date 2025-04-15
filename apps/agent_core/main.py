from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🤖 Agent Core is alive"}

if __name__ == "__main__":
    port = int(os.getenv("AGENT_CORE_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
