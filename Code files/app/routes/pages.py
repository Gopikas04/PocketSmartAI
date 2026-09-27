from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import get_optional_user
from app.models.db_models import User

templates=Jinja2Templates(directory="app/templates")
router=APIRouter()

def render(request,template,**context):
    return templates.TemplateResponse(template,{"request":request,**context})

@router.get("/",response_class=HTMLResponse)
def home(request:Request,user:User|None=Depends(get_optional_user)):
    return render(request,"index.html",user=user)

@router.get("/testimonials",response_class=HTMLResponse)
def testimonials(request:Request,user:User|None=Depends(get_optional_user)):
    return render(request,"testimonials.html",user=user)

@router.get("/register",response_class=HTMLResponse)
def register(request:Request): return render(request,"register.html",user=None)

@router.get("/login",response_class=HTMLResponse)
def login(request:Request): return render(request,"login.html",user=None)

def protected(template):
    def handler(request:Request,user:User|None=Depends(get_optional_user)):
        return RedirectResponse("/login",303) if not user else render(request,template,user=user)
    return handler

for path,template in [("/dashboard","dashboard.html"),("/home-planner","home_planner.html"),
                      ("/party-planner","party_planner.html"),("/jewelry-planner","jewelry_planner.html"),
                      ("/history-page","history.html"),("/recommendations","recommendations.html")]:
    router.add_api_route(path,protected(template),methods=["GET"],response_class=HTMLResponse)
