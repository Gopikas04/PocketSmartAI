import json
import re
from typing import Any
from app.core.config import settings

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

SYSTEM_INSTRUCTION = r"""
You are PocketSmart AI, a budget-aware recommendation assistant.
Return ONLY valid JSON, with no markdown.
Never claim you queried private retailer databases or live inventory.
Use INR (₹). Keep recommendations within the user's total budget.
Use only these platform names where appropriate: Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO.
Output exactly:
{
  "title": "string",
  "summary": "string",
  "allocation": [{"category": "string", "amount": 0, "percentage": 0}],
  "recommendations": [{
    "category": "string",
    "name": "string",
    "description": "string",
    "estimated_price": 0,
    "quantity": 1,
    "platform": "Amazon",
    "search_query": "string",
    "reason": "string"
  }]
}
"""

def _extract_json(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None

def generate_recommendation(prompt, image_bytes=None, mime_type=None):
    if not settings.gemini_api_key or genai is None:
        return None
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        parts = [types.Part.from_text(text=SYSTEM_INSTRUCTION + "\n\n" + prompt)]
        if image_bytes and mime_type:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=parts,
            config=types.GenerateContentConfig(
                temperature=settings.gemini_temperature,
                response_mime_type="application/json",
            ),
        )
        return _extract_json(response.text)
    except Exception:
        return None

def build_home_prompt(data):
    return f"""Create a home interior budget plan.
Total budget: ₹{data["budget"]:,.2f}
Style: {data["style"]}
Requested items: {json.dumps(data["rooms"], ensure_ascii=False)}
Notes: {data.get("notes", "")}
Allocate budget across essentials, lighting/fans and decor. Respect quantities.
Recommend practical options from Amazon, Flipkart and/or IKEA.
"""

def build_party_prompt(data):
    return f"""Create a party budget plan.
Budget: ₹{data["budget"]:,.2f}
Guests: {data["guests"]}
Event type: {data["event_type"]}
Venue: {data.get("venue_details", "")}
Location: {data.get("location", "")}
Food preference: {data.get("food_preference", "Mixed")}
Notes: {data.get("notes", "")}
Allocate proportionally across food/catering, venue, decoration and entertainment.
Use Swiggy, Zomato, OYO and suitable shopping platforms.
"""

def build_jewelry_prompt(data):
    return f"""Create a jewelry recommendation plan.
Budget: ₹{data["budget"]:,.2f}
Occasion: {data["occasion"]}
Style: {data["style"]}
Outfit description: {data.get("outfit_description", "")}
Notes: {data.get("notes", "")}
Recommend coordinated jewelry from Amazon and Flipkart. If an image is attached,
consider broad colors, neckline/visual balance and style without identifying the person.
"""

def fallback_home(data):
    b = float(data["budget"])
    return {
        "title": "Home Interior Budget Plan",
        "summary": "A practical starter allocation across essentials, lighting, decor and contingency.",
        "allocation": [
            {"category":"Furniture & essentials","amount":round(b*.45,2),"percentage":45},
            {"category":"Lighting & fans","amount":round(b*.25,2),"percentage":25},
            {"category":"Decor","amount":round(b*.20,2),"percentage":20},
            {"category":"Contingency","amount":round(b*.10,2),"percentage":10},
        ],
        "recommendations": [
            {
                "category": x["room"],
                "name": f'{data["style"]} {x["item"]}',
                "description": f'Budget-conscious {x["item"]} option for the {x["room"]}.',
                "estimated_price": round(min(b/max(len(data["rooms"]),1)/x["quantity"],b),2),
                "quantity": x["quantity"],
                "platform": "IKEA" if x["item"].lower() in {"dining table","side table","wardrobe","shelf"} else "Amazon",
                "search_query": f'{data["style"]} {x["item"]} {x["room"]}',
                "reason": "Matches the requested room, style and quantity."
            } for x in data["rooms"]
        ],
    }

def fallback_party(data):
    b=float(data["budget"]); g=int(data["guests"])
    return {
        "title": f'{data["event_type"].title()} Party Budget Plan',
        "summary": f"A balanced plan for {g} guests within the stated budget.",
        "allocation":[
            {"category":"Food & catering","amount":round(b*.50,2),"percentage":50},
            {"category":"Venue","amount":round(b*.20,2),"percentage":20},
            {"category":"Decoration","amount":round(b*.15,2),"percentage":15},
            {"category":"Entertainment","amount":round(b*.10,2),"percentage":10},
            {"category":"Contingency","amount":round(b*.05,2),"percentage":5},
        ],
        "recommendations":[
            {"category":"Food","name":f'{data["food_preference"]} catering for {g} guests',"description":"Compare local catering and restaurant options.","estimated_price":round(b*.50,2),"quantity":1,"platform":"Zomato","search_query":f'{data["food_preference"]} catering {g} guests {data.get("location","")}',"reason":"Guest count directly affects catering cost."},
            {"category":"Venue","name":"Event-friendly venue options","description":"Compare venue/accommodation options.","estimated_price":round(b*.20,2),"quantity":1,"platform":"OYO","search_query":f'event venue {data.get("location","")}',"reason":"Keeps venue spending within the plan."},
            {"category":"Decoration","name":"Theme decoration package","description":"Search event decoration supplies and packages.","estimated_price":round(b*.15,2),"quantity":1,"platform":"Amazon","search_query":f'{data["event_type"]} party decoration',"reason":"Provides a theme-focused decor allowance."},
        ],
    }

def fallback_jewelry(data):
    b=float(data["budget"])
    return {
        "title": f'{data["occasion"].title()} Jewelry Plan',
        "summary":"Coordinated jewelry suggestions based on occasion, style and budget.",
        "allocation":[
            {"category":"Main piece","amount":round(b*.55,2),"percentage":55},
            {"category":"Earrings","amount":round(b*.25,2),"percentage":25},
            {"category":"Bracelet/Ring","amount":round(b*.15,2),"percentage":15},
            {"category":"Contingency","amount":round(b*.05,2),"percentage":5},
        ],
        "recommendations":[
            {"category":"Necklace","name":f'{data["style"]} statement necklace',"description":"A coordinated main piece for the occasion.","estimated_price":round(b*.55,2),"quantity":1,"platform":"Amazon","search_query":f'{data["occasion"]} {data["style"]} necklace',"reason":"Main piece receives the largest allocation."},
            {"category":"Earrings","name":f'{data["style"]} matching earrings',"description":"Earrings designed to complement the main piece.","estimated_price":round(b*.25,2),"quantity":1,"platform":"Flipkart","search_query":f'{data["occasion"]} {data["style"]} earrings',"reason":"Adds coordination without consuming the full budget."},
        ],
    }
