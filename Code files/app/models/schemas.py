from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HomeItem(BaseModel):
    room: str = Field(min_length=2, max_length=50)
    item: str = Field(min_length=2, max_length=100)
    quantity: int = Field(ge=1, le=50)

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    style: str = Field(min_length=2, max_length=80)
    rooms: list[HomeItem] = Field(min_length=1, max_length=30)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    guests: int = Field(ge=1, le=100000)
    event_type: str = Field(min_length=2, max_length=80)
    venue_details: str = Field(default="", max_length=1000)
    location: str = Field(default="", max_length=120)
    food_preference: str = Field(default="Mixed", max_length=80)
    notes: str = Field(default="", max_length=1000)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="Elegant", min_length=2, max_length=80)
    outfit_description: str = Field(default="", max_length=1000)
    notes: str = Field(default="", max_length=1000)

class RecommendationResponse(BaseModel):
    recommendation_id: int
    planner_type: Literal["home", "party", "jewelry"]
    title: str
    summary: str
    budget: float
    allocation: list[dict]
    recommendations: list[dict]
    ai_used: bool
    created_at: str
