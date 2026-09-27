from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_current_user, hash_password
from app.models.db_models import Recommendation, User
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut

router=APIRouter()

def set_cookie(response,token):
    response.set_cookie("access_token",token,httponly=True,samesite="lax",secure=False,max_age=86400)

@router.post("/register",response_model=UserOut,status_code=201)
def register(payload:RegisterRequest,db:Session=Depends(get_db)):
    email=payload.email.lower()
    if db.query(User).filter(User.email==email).first():
        raise HTTPException(409,"An account with this email already exists.")
    user=User(name=payload.name.strip(),email=email,password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login")
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    user=authenticate_user(db,payload.email,payload.password)
    if not user: raise HTTPException(401,"Invalid email or password.")
    response=JSONResponse({"message":"Login successful","user":UserOut.model_validate(user).model_dump()})
    set_cookie(response,create_access_token(user.id))
    return response

@router.post("/token",response_model=TokenResponse)
def token(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=authenticate_user(db,form.username,form.password)
    if not user: raise HTTPException(401,"Incorrect username or password.")
    return TokenResponse(access_token=create_access_token(user.id))

@router.get("/logout")
def logout(request:Request):
    response=RedirectResponse("/login",303); response.delete_cookie("access_token"); request.session.clear(); return response

@router.get("/session-info")
def session_info(user:User=Depends(get_current_user)):
    return {"authenticated":True,"user":UserOut.model_validate(user).model_dump()}

@router.get("/session-data")
def session_data(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(Recommendation).filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).limit(5).all()
    return {"user":UserOut.model_validate(user).model_dump(),"recent_recommendations":[
        {"id":r.id,"planner_type":r.planner_type,"title":r.result_data.get("title","Recommendation"),"created_at":r.created_at.isoformat()}
        for r in rows
    ]}
