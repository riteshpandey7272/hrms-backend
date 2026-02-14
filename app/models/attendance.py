from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Employee ID")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    status: Literal["Present", "Absent"] = Field(..., description="Attendance status")


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str | None = None
    date: str
    status: str
    created_at: datetime
