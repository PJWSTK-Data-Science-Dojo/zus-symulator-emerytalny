from typing import Literal
from pydantic import BaseModel, ConfigDict,Field


class RetirementExpectations(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["f", "m", "x"]
    expected_retirement_income: float = Field(..., gt=0)
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
   age: int = Field(..., ge=0, le=120)
   sex: Literal["f", "m", "x"]
   include_sick: bool
   
   work_blocks: list[WorkBlock]
   
class RetirementCalcOutput(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   realistic_retirement_income: float = Field(..., gt=0)
   actual_retirement_income: float = Field(..., gt=0)
   