from datetime import datetime, datetime, timezone
from typing import Literal, Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi.params import Depends
from sqlalchemy import Enum
from db import engine, Base, get_session, DATABASE_URL
from pydantic import BaseModel, Field, ConfigDict, confloat, conint, condecimal
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import uuid
import os


from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()  # załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_admin, create_access_token, create_refresh_token,
    refresh_pair, require_admin_from_bearer
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class RetirementExpectations(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["f", "m", "x"]
    expected_retirement_income: float = Field(..., gt=0)
    include_sick: bool
    funds: float = Field(..., ge=0)
    start_year: int = Field(..., ge=1900, le=2100)
    expected_retirement_age: int = Field(..., ge=0, le=120)
    
class RetirementPlan(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   expected_total_funds: float = Field(..., gt=0)
   funds_left_to_collect: float = Field(..., gt=0)
   
   
class WorkBlock(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   years: float = Field(..., gt=0)
   gross_income: float = Field(..., gt=0)
   contribution_rate: float = Field(..., gt=0, le=1)

class RetirementCalcInput(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   work_blocks: list[WorkBlock]
   
class RetirementCalcOutput(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   pension: float = Field(..., gt=0)
   
   
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/generate_retirement_plan", response_model=RetirementPlan)
async def retirement_plan(expectations: RetirementExpectations, db=Depends(get_session)):
    return RetirementPlan(
        expected_total_funds=100_000.,
        total_funds=expectations.funds
    )

@app.post("/calc_retirement_income", response_model=RetirementCalcOutput)
async def calc_retirement_income(expectations: RetirementExpectations, db=Depends(get_session)):
    return RetirementCalcOutput(
        pension=4500.0
    )

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str


@app.post("/token", response_model=TokenPair)
def obtain_token_pair(credentials: LoginRequest):
    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Błędny login lub hasło")
    return TokenPair(
        access_token=create_access_token(credentials.username),
        refresh_token=create_refresh_token(credentials.username),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/refresh_token", response_model=TokenPair)
def refresh_tokens(req: RefreshRequest):
    try:
        access, refresh = refresh_pair(req.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.get("/me")
def me(token: str = Depends(oauth2_scheme)):
    admin = require_admin_from_bearer(token)
    return {"role": "admin", "username": admin}