from fastapi import FastAPI
app=FastAPI(title="NorthStar")
@app.get("/")
def root():
    return {"app":"NorthStar","version":"0.1"}
@app.get("/health")
def health():
    return {"status":"ok"}
