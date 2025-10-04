from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.params import Depends
from db.repositories.report import ReportRepository
from schemas.auth import RefreshRequest, TokenPair
from schemas.report import ReportCreate
from schemas.simulations import RetirementCalcInput, RetirementCalcOutput, RetirementExpectations, RetirementPlan
import numpy as np
from db import engine, Base, get_session

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv

load_dotenv()  # załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_admin, create_access_token, create_refresh_token,
    refresh_pair, require_admin_from_bearer
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



   
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
    
    expected_total_funds = 100000
    funds_left_to_collect = expected_total_funds / 2
    
    report_repo = ReportRepository(db)
    
    report_data = ReportCreate(
        sim_type="RETIRE_PLAN",
        age=expectations.age,
        sex=expectations.sex,
        expected_retirement_income=expectations.expected_retirement_income,
        include_sick=expectations.include_sick,
        funds=expectations.funds,
        start_year=expectations.start_year,
        expected_retirement_age=expectations.expected_retirement_age,
        
    )
    new_report = await report_repo.create(report_data)
    return RetirementPlan(
        expected_total_funds=expected_total_funds,
        funds_left_to_collect=funds_left_to_collect,
    )

@app.post("/calc_retirement_income", response_model=RetirementCalcOutput)
async def calc_retirement_income(data: RetirementCalcInput, db=Depends(get_session)):
    actual_retirement_income = 4000.0
    realistic_retirement_income = 4500.0
    
    salaries = [block.gross_income for block in data.work_blocks]
    weights = [block.years for block in data.work_blocks]
    weighted_avg = np.average(salaries, weights=weights)

    report_repo = ReportRepository(db)
    report_data = ReportCreate(
        sim_type="PENSION_CALC",
        age=data.age,
        sex=data.sex,
        realistic_retirement_income=realistic_retirement_income,
        actual_retirement_income=actual_retirement_income,
        salary=weighted_avg
    )
    
    new_report = await report_repo.create(report_data)

    return RetirementCalcOutput(
        realistic_retirement_income=realistic_retirement_income,
        actual_retirement_income=actual_retirement_income
    )


@app.get("/reports", response_model=list[ReportCreate])
async def get_reports(db=Depends(get_session), token: str = Depends(oauth2_scheme)):
    require_admin_from_bearer(token)
    report_repo = ReportRepository(db)
    return await report_repo.get_all()

@app.post("/token", response_model=TokenPair)
def obtain_token_pair(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if not authenticate_admin(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Błędny login lub hasło",
        )

    return TokenPair(
        access_token=create_access_token(username),
        refresh_token=create_refresh_token(username),
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