from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routes import employees, attendance


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="HRMS Lite API",
    description="Lightweight Human Resource Management System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error["msg"]

        # validation errors
        if "email" in field.lower() and "valid" in msg.lower():
            errors.append("Invalid email format")
        elif "missing" in msg.lower():
            errors.append(f"{field} is required")
        elif "at least" in msg.lower():
            errors.append(f"{field} cannot be empty")
        elif "match" in msg.lower() or "pattern" in msg.lower():
            errors.append(f"{field} has invalid format")
        else:
            errors.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=400,
        content={"detail": errors[0] if len(errors) == 1 else "; ".join(errors)},
    )


# handler for unexpected server errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


app.include_router(employees.router)
app.include_router(attendance.router)


@app.get("/")
async def root():
    return {"message": "HRMS Lite API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
