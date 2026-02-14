from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.models.employee import EmployeeCreate, EmployeeResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(employee: EmployeeCreate):
    db = get_db()

    existing = await db.employees.find_one({"employee_id": employee.employee_id})
    if existing:
        raise HTTPException(status_code=409, detail=f"Employee with ID '{employee.employee_id}' already exists")

    existing_email = await db.employees.find_one({"email": employee.email})
    if existing_email:
        raise HTTPException(status_code=409, detail=f"Employee with email '{employee.email}' already exists")

    doc = {
        **employee.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.employees.insert_one(doc)

    return EmployeeResponse(
        id=str(result.inserted_id),
        employee_id=doc["employee_id"],
        full_name=doc["full_name"],
        email=doc["email"],
        department=doc["department"],
        created_at=doc["created_at"],
    )


@router.get("", response_model=list[EmployeeResponse])
async def list_employees():
    db = get_db()
    employees = []
    async for emp in db.employees.find().sort("created_at", -1):
        employees.append(
            EmployeeResponse(
                id=str(emp["_id"]),
                employee_id=emp["employee_id"],
                full_name=emp["full_name"],
                email=emp["email"],
                department=emp["department"],
                created_at=emp["created_at"],
            )
        )
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    db = get_db()
    emp = await db.employees.find_one({"employee_id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")

    return EmployeeResponse(
        id=str(emp["_id"]),
        employee_id=emp["employee_id"],
        full_name=emp["full_name"],
        email=emp["email"],
        department=emp["department"],
        created_at=emp["created_at"],
    )


@router.delete("/{employee_id}", status_code=200)
async def delete_employee(employee_id: str):
    db = get_db()
    result = await db.employees.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")

    await db.attendance.delete_many({"employee_id": employee_id})

    return {"message": f"Employee '{employee_id}' deleted successfully"}
