from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User
from app.models.schemas import HomeRequest, PartyRequest
from app.services.recommendation_service import generate_home, generate_party, generate_jewelry

router=APIRouter()

def response(row):
    r=row.result_data
    return {"recommendation_id":row.id,"planner_type":row.planner_type,"title":r.get("title","PocketSmart Plan"),
            "summary":r.get("summary",""),"budget":float(row.input_data.get("budget",0)),
            "allocation":r.get("allocation",[]),"recommendations":r.get("recommendations",[]),
            "ai_used":bool(r.get("ai_used")),"created_at":row.created_at.isoformat()}

@router.post("/generate-home")
def generate_home_route(payload:HomeRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return response(generate_home(db,user.id,payload.model_dump()))

@router.post("/generate-party")
def generate_party_route(payload:PartyRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return response(generate_party(db,user.id,payload.model_dump()))

@router.post("/generate-jewelry")
async def generate_jewelry_route(
    budget:float=Form(...),occasion:str=Form(...),style:str=Form("Elegant"),
    outfit_description:str=Form(""),notes:str=Form(""),
    outfit_image:UploadFile|None=File(None),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if budget<=0 or budget>100_000_000: raise HTTPException(422,"Budget must be greater than zero and within the supported range.")
    if not occasion.strip(): raise HTTPException(422,"Occasion is required.")
    image_bytes=image_filename=mime_type=None
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in {"image/jpeg","image/png","image/webp"}:
            raise HTTPException(415,"Only JPG, PNG and WEBP images are supported.")
        image_bytes=await outfit_image.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024:
            raise HTTPException(413,f"Image must be smaller than {settings.max_upload_mb} MB.")
        image_filename=f"{uuid4().hex}_{Path(outfit_image.filename).name}"
        mime_type=outfit_image.content_type
    data={"budget":budget,"occasion":occasion.strip(),"style":style.strip(),
          "outfit_description":outfit_description.strip(),"notes":notes.strip()}
    return response(generate_jewelry(db,user.id,data,image_bytes,mime_type,image_filename))
