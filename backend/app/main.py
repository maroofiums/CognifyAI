from fastapi import FastAPI

app = FastAPI(
    title="CognifyAI",
    description="AI Code Optimiser",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "CognifyAI is running..."}

@app.get("/health")
def health():
    return {"status": "ok"}
