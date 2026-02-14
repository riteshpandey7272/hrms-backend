# HRMS Lite - Backend

REST API backend for the HRMS Lite application, built with FastAPI and MongoDB.

## Tech Stack

- **Framework:** FastAPI
- **Database:** MongoDB (async via Motor)
- **Validation:** Pydantic v2
- **Server:** Uvicorn (ASGI)

## Project Structure

```
app/
├── main.py           # App entry point & middleware
├── database.py       # MongoDB connection
├── models/           # Pydantic schemas
└── routes/           # API route handlers
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hrms_lite
```

Start the server:

```bash
uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`.

## API Endpoints

**Employees** — `/api/employees`

- `POST /` — Create employee
- `GET /` — List all employees
- `GET /:employee_id` — Get by ID
- `DELETE /:employee_id` — Delete employee

**Attendance** — `/api/attendance`

- `POST /` — Mark attendance
- `GET /` — List records (filter by `date`, `employee_id`)
- `GET /employee/:employee_id` — Get employee attendance
- `GET /summary/today` — Today's summary

**Health** — `GET /` | `GET /health`

Full interactive docs available at `/docs` (Swagger) and `/redoc`.
