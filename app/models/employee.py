from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Unique employee ID")
    full_name: str = Field(..., min_length=1, description="Full name of employee")
    email: EmailStr = Field(..., description="Email address")
    department: str = Field(..., min_length=1, description="Department name")


class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime
