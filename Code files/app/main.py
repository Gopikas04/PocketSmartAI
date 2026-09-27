from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.routes import auth,history,pages,planners

app=FastAPI(title=settings.app_name,version="1.0.0",
            description="Budget-aware AI recommendations for home, party and jewelry planning.")

app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_middleware(SessionMiddleware,secret_key=settings.secret_key,max_age=settings.session_max_age,same_site="lax",https_only=False)
app.mount("/static",StaticFiles(directory="app/static"),name="static")

@app.on_event("startup")
def startup():
    Path("data").mkdir(exist_ok=True); Path("uploads").mkdir(exist_ok=True); init_db()

@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}

@app.get("/startup")
def startup_status():
    return {"status":"ready","database":"configured","gemini_configured":bool(settings.gemini_api_key),"model":settings.gemini_model}

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("app.main:app",host="127.0.0.1",port=8000,reload=True)
