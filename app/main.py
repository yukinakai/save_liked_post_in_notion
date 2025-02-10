from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Save Liked Post in Notion")

class Tweet(BaseModel):
    text: str
    username: str
    tweet_url: str
    created_at: str
    embed_code: str

@app.get("/")
async def root():
    return {"message": "Welcome to Save Liked Post in Notion API"}

@app.get("/webhook")
async def webhook_get():
    return {"message": "Hello World"}

@app.post("/webhook")
async def webhook_post():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
