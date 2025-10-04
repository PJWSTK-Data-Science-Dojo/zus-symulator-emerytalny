from typing import Literal
from fastapi import FastAPI

from fastapi import FastAPI
from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi.params import Depends
from sqlalchemy import Enum
from db import engine, Base, get_session, DATABASE_URL
from pydantic import BaseModel, Field, ConfigDict, confloat, conint, condecimal

    
class RetirementExpectations(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["f", "m", "x"]
    expected_retirement_income: float = Field(..., gt=0)
    include_sick: bool
    funds: float = Field(..., ge=0)
    start_year: int = Field(..., ge=1900, le=2100)
    expected_retirement_age: int = Field(..., ge=0, le=120)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Connecting to database at {DATABASE_URL}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/generate_retirement_plan")
async def retirement_plan(expectations: RetirementExpectations, db=Depends(get_session)):
    return {"expected_salary": 10000, "year_to_work": 20}