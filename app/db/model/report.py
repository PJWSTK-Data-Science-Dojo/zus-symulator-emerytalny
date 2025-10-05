from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
import enum
from db.base import Base

class SimType(str, enum.Enum):
    RETIRE_PLAN = "RETIRE_PLAN"  # Plan emerytalny na podstawie oczekiwań
    PENSION_CALC = "PENSION_CALC"    # Kalkulator emerytalny od historii zarobków

class Sex(str, enum.Enum):
    F = "f"
    M = "m"
    X = "x"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Metadane
    sim_type = Column(Enum(SimType), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    salary = Column(Float, nullable=True)
    sick_leave = Column(Boolean, default=False, nullable=False)

    # Pola opcjonalne
    accumulated_funds = Column(Float, nullable=True)  # fakultatywne
    postal_code = Column(String, nullable=True)       # opcjonalne

    # Wyniki (zależne od sim_type)
    expected_retirement_income = Column(Float, nullable=True)   # tylko EXPECTED
    actual_retirement_income = Column(Float, nullable=True)     # tylko HISTORY
    realistic_retirement_income = Column(Float, nullable=True) 