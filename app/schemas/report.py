from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from enum import Enum


# --- Base ---
class ReportBase(BaseModel):
    sim_type: Literal["RETIRE_PLAN", "PENSION_CALC"]
    age: int
    sex: Literal["f", "m", "x"]
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
    pass

# --- Read / Out ---
class ReportOut(ReportBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info):
        # format: "YYYY-MM-DD HH:MM:SS"
        return value.strftime("%Y-%m-%d %H:%M:%S")
