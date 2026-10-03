from fastapi import FastAPI
import uvicorn
from app.web_workflow.router import router

app = FastAPI(title="ASTRA - Web Workflow API")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
