from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum

# Te same enumy co w modelu
class SimType(str, Enum):
    EXPECTED = "EXPECTED"  # Plan emerytalny na podstawie oczekiwań
    HISTORY = "HISTORY"    # Kalkulator emerytalny od historii zarobków

class Gender(str, Enum):
    K = "K"
    M = "M"

# --- Base ---
class ReportBase(BaseModel):
    sim_type: SimType
    age: int
    gender: Gender
    sick_leave: bool = False

    salary: Optional[float] = None

    accumulated_funds: Optional[float] = None
    postal_code: Optional[str] = None

    expected_retirement_income: Optional[float] = None
    actual_retirement_income: Optional[float] = None
    realistic_retirement_income: Optional[float] = None

# --- Create ---
class ReportCreate(ReportBase):
    pass

# --- Update (partial) ---
class ReportUpdate(BaseModel):
    sim_type: Optional[SimType] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    salary: Optional[float] = None
    sick_leave: Optional[bool] = None

    accumulated_funds: Optional[float] = None
    postal_code: Optional[str] = None

    expected_retirement_income: Optional[float] = None
    actual_retirement_income: Optional[float] = None
    realistic_retirement_income: Optional[float] = None

# --- Read / Out ---
class ReportOut(ReportBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)