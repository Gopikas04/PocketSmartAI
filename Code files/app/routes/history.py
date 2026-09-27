from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import Recommendation, User

router=APIRouter()

@router.get("/history")
def history(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(Recommendation).filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).all()
    return [{"id":r.id,"planner_type":r.planner_type,"title":r.result_data.get("title","Recommendation"),
             "summary":r.result_data.get("summary",""),"budget":r.input_data.get("budget",0),
             "created_at":r.created_at.isoformat()} for r in rows]

@router.get("/recommendations-details/{recommendation_id}")
def details(recommendation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.query(Recommendation).filter(Recommendation.id==recommendation_id,Recommendation.user_id==user.id).first()
    if not r: raise HTTPException(404,"Recommendation not found.")
    return {"id":r.id,"planner_type":r.planner_type,"input":r.input_data,"result":r.result_data,"created_at":r.created_at.isoformat()}
