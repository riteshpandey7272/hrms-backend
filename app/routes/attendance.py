from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models.attendance import AttendanceCreate, AttendanceResponse
from datetime import datetime, timezone
from typing import Optional

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("", response_model=AttendanceResponse, status_code=201)
async def mark_attendance(attendance: AttendanceCreate):
    db = get_db()

    # Verify employee exists or not
    employee = await db.employees.find_one({"employee_id": attendance.employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee '{attendance.employee_id}' not found")

    # Check for duplicate attendance of employee
    existing = await db.attendance.find_one({
        "employee_id": attendance.employee_id,
        "date": attendance.date,
    })
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Attendance already marked for employee '{attendance.employee_id}' on {attendance.date}",
        )

    doc = {
        **attendance.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.attendance.insert_one(doc)

    return AttendanceResponse(
        id=str(result.inserted_id),
        employee_id=doc["employee_id"],
        employee_name=employee["full_name"],
        date=doc["date"],
        status=doc["status"],
        created_at=doc["created_at"],
    )


@router.get("", response_model=list[AttendanceResponse])
async def list_attendance(
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Filter by date"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
):
    db = get_db()
    query = {}
    if date:
        query["date"] = date
    if employee_id:
        query["employee_id"] = employee_id

    emp_names = {}
    async for emp in db.employees.find():
        emp_names[emp["employee_id"]] = emp["full_name"]

    records = []
    async for rec in db.attendance.find(query).sort("date", -1):
        records.append(
            AttendanceResponse(
                id=str(rec["_id"]),
                employee_id=rec["employee_id"],
                employee_name=emp_names.get(rec["employee_id"]),
                date=rec["date"],
                status=rec["status"],
                created_at=rec["created_at"],
            )
        )
    return records


@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
async def get_employee_attendance(employee_id: str):
    db = get_db()

    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")

    records = []
    async for rec in db.attendance.find({"employee_id": employee_id}).sort("date", -1):
        records.append(
            AttendanceResponse(
                id=str(rec["_id"]),
                employee_id=rec["employee_id"],
                employee_name=employee["full_name"],
                date=rec["date"],
                status=rec["status"],
                created_at=rec["created_at"],
            )
        )
    return records


@router.get("/summary/today")
async def today_summary():
    db = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_employees = await db.employees.count_documents({})
    present_today = await db.attendance.count_documents({"date": today, "status": "Present"})
    absent_today = await db.attendance.count_documents({"date": today, "status": "Absent"})

    return {
        "date": today,
        "total_employees": total_employees,
        "present": present_today,
        "absent": absent_today,
        "not_marked": total_employees - present_today - absent_today,
    }
