from contextlib import asynccontextmanager
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel

from data.functionalities.fun_facts import FunFacts
from data.functionalities.pension_calculator import PensionCalculator, PensionInputs
from data.functionalities.pension_delay import PensionDelayCalculator
from data.functionalities.sick_leave_adjustment import SickLeaveAdjustment
from db import Base, engine, get_session
from db.repositories.report import ReportRepository
from schemas.auth import RefreshRequest, TokenPair
from schemas.report import ReportCreate, ReportOut
from schemas.simulations import RetirementCalcInput, RetirementCalcOutput, RetirementExpectations, RetirementPlan

load_dotenv()  # załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_admin,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_token,
    refresh_pair,
    require_admin_from_bearer,
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
    expected_life_expectancy_years = 82 if expectations.sex == "f" else 78
    years_to_collect = expected_life_expectancy_years - expectations.expected_retirement_age
    months_to_collect = max(60, years_to_collect * 12)
    total_funds = expectations.expected_retirement_income * months_to_collect
    funds_left_to_collect = max(0, total_funds - expectations.funds)

    report_repo = ReportRepository(db)

    report_data = ReportCreate(
        sim_type="RETIRE_PLAN",
        age=expectations.age,
        sex=expectations.sex,
        expected_retirement_income=expectations.expected_retirement_income,
        funds=expectations.funds,
        start_year=expectations.start_year,
        expected_retirement_age=expectations.expected_retirement_age,
    )
    new_report = await report_repo.create(report_data)
    return RetirementPlan(
        expected_total_funds=total_funds,
        funds_left_to_collect=funds_left_to_collect,
    )


@app.post("/calc_retirement_income", response_model=RetirementCalcOutput)
async def calc_retirement_income(data: RetirementCalcInput, db=Depends(get_session)):
    salaries = [block.gross_income for block in data.work_blocks]
    weights = [block.years for block in data.work_blocks]
    weighted_avg = np.average(salaries, weights=weights)
    total_capital = sum(block.gross_income * block.contribution_rate * block.years * 12 for block in data.work_blocks)

    if data.sex == "f":
        life_expectancy_years = 82
        retirement_age = 60
    else:
        life_expectancy_years = 78
        retirement_age = 65

    months_to_live = max(60, life_expectancy_years - retirement_age) * 12

    year_of_retirement = datetime.now().year + (data.age - retirement_age)
    total_capital = SickLeaveAdjustment.calculate(total_capital)
    inp = PensionInputs(
        life_expectancy_months=months_to_live,
        total_capital=total_capital,
    )

    actual_retirement_income = PensionCalculator.calculate_pension(inp)

    realistic_retirement_income = actual_retirement_income * 0.6
    replacement_rate = (realistic_retirement_income / weighted_avg) * 100 if weighted_avg > 0 else 0
    report_repo = ReportRepository(db)
    report_data = ReportCreate(
        sim_type="PENSION_CALC",
        age=data.age,
        sex=data.sex,
        realistic_retirement_income=realistic_retirement_income,
        actual_retirement_income=actual_retirement_income,
        salary=weighted_avg,
    )
    sick_salary = SickLeaveAdjustment.calculate(actual_retirement_income)

    new_report = await report_repo.create(report_data)
    result = {
        "actual_pension": actual_retirement_income,
        "realistic_pension": realistic_retirement_income,
        "replacement_rate": replacement_rate,
        "average_pension": 4045.20,
        "salary_with_sickness": sick_salary,
        "salary_without_sickness": actual_retirement_income,
        "pension_increase": PensionDelayCalculator.calculate_pension_delay(
            base_capital=total_capital,
            monthly_contribution=weighted_avg * 0.195,  # 19.5% składka emerytalna
            life_expectancy_months=months_to_live,
        ),
    }

    return result


@app.get("/reports", response_model=list[ReportOut])
async def get_reports(db=Depends(get_session)):
    report_repo = ReportRepository(db)
    return await report_repo.get_all()


class LoginModel(BaseModel):
    username: str
    password: str


@app.post("/token", response_model=TokenPair)
def obtain_token_pair(form_data: LoginModel):
    print("Obtaining token pair for user:", form_data.username)
    if not authenticate_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Błędny login lub hasło",
        )

    return TokenPair(
        access_token=create_access_token(form_data.username),
        refresh_token=create_refresh_token(form_data.username),
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


@app.get("/fun_fact")
def get_fun_fact():
    fact = FunFacts.get_random_fact()
    return {"fun_fact": fact}
