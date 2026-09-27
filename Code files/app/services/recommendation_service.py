from app.models.db_models import Recommendation
from app.services.ai_service import (
    build_home_prompt, build_party_prompt, build_jewelry_prompt,
    fallback_home, fallback_party, fallback_jewelry, generate_recommendation,
)
from app.services.platform_links import attach_platform_links

def _finish(result, budget, ai_used):
    result = dict(result)
    result["allocation"] = result.get("allocation") or []
    result["recommendations"] = attach_platform_links(result.get("recommendations") or [])
    total = sum(float(x.get("estimated_price",0))*max(1,int(x.get("quantity",1))) for x in result["recommendations"])
    if total > budget and total > 0:
        factor = budget/total
        for x in result["recommendations"]:
            x["estimated_price"] = round(float(x["estimated_price"])*factor,2)
    result["ai_used"] = ai_used
    return result

def save_recommendation(db, user_id, planner_type, input_data, result, image_filename=None):
    row=Recommendation(user_id=user_id,planner_type=planner_type,input_data=input_data,result_data=result,image_filename=image_filename)
    db.add(row); db.commit(); db.refresh(row)
    return row

def generate_home(db,user_id,data):
    ai=generate_recommendation(build_home_prompt(data))
    result=_finish(ai or fallback_home(data),data["budget"],ai is not None)
    return save_recommendation(db,user_id,"home",data,result)

def generate_party(db,user_id,data):
    ai=generate_recommendation(build_party_prompt(data))
    result=_finish(ai or fallback_party(data),data["budget"],ai is not None)
    return save_recommendation(db,user_id,"party",data,result)

def generate_jewelry(db,user_id,data,image_bytes=None,mime_type=None,image_filename=None):
    ai=generate_recommendation(build_jewelry_prompt(data),image_bytes,mime_type)
    result=_finish(ai or fallback_jewelry(data),data["budget"],ai is not None)
    return save_recommendation(db,user_id,"jewelry",data,result,image_filename)
