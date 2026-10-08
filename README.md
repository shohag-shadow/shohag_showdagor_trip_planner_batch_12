# Trip Planner API

A REST API for planning group trips: create trips with a budget and a
traveler limit, invite travelers, track expenses, and move a trip through its
lifecycle (planned → ongoing → completed / cancelled).

There is no UI — this is a pure JSON API built with **Python + Flask +
Flask-SQLAlchemy**, backed by **SQLite**.

## Problem statement

Coordinating a group trip means keeping several rules straight: who is coming,
whether the group has room, whether a person is double-booked across two trips
with overlapping dates, and whether the spending is still within budget. The
API centralizes those rules in one place so any client (web, mobile, CLI) gets
the same validation and the same consistent state.

## Prerequisites

- **Python 3.10+** with `venv` support (the code uses modern type/`str` f-string syntax).
- No database server needed — SQLite is bundled with Python.
- Git to clone the project (Not reqired if you can download the project as zip from github and unzip it and use it)

## Run instructions
Run thease commands in the terminal (linux)

```bash
git clone https://github.com/shohag-shadow/shohag_showdagor_trip_planner_batch_12.git
cd shohag_showdagor_trip_planner_batch_12
./run.sh
```

If you get "permission denied", run `chmod +x run.sh` first. then run `./run.sh`

## Fresh-clone run instructions (run this command if you already cloned the project or unzipped it from zip)

From the project root:

```bash
./run.sh
```
If you get "permission denied", run `chmod +x run.sh` first.  

`run.sh` performs the full bootstrap, then starts the server:

1. Creates a `.venv` virtual environment if one does not exist.
2. Creates the `instance/` directory if it does not exist (where the SQLite file lives).
3. Copies `.env.example` to `.env` if `.env` is missing.
4. Installs dependencies from `requirements.txt`.
5. Runs the test suite (`pytest test.py -v`).
6. Starts the app with `python run.py`.

The server then listens on **http://localhost:5000** (or the `PORT` set in `.env`).

> `run.sh` uses `set -e`, so if the tests or install fail, the server will not start.

## Manual run instructions

If you prefer to run the steps yourself (e.g. on Windows without bash):

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local env file
cp .env.example .env

# 4. (optional) run the tests
pytest test.py -v

# 5. Start the server
python run.py
```

Environment variables (see `.env.example`):

| Variable        | Default            | Purpose                                   |
| --------------- | ------------------ | ----------------------------------------- |
| `FLASK_DEBUG`   | `True`            | Enables Flask debug/reloader when `True`. |
| `DATABASE_NAME` | `trip_planner.db`  | SQLite file name inside `instance/`.      |
| `PORT`          | `5000`             | Port the dev server binds to.             |

## API endpoint table

Base URL: `http://localhost:5000`. All API routes are prefixed with `/api/v1`. All id are `integer` type

| Method   | Path                                        | Description                              | Success | Common errors |
| -------- | ------------------------------------------- | ---------------------------------------- | ------- | ------------- |
| `GET`    | `/health`                                   | Liveness check                           | `200`   | — |
| `GET`    | `/api/v1/trips`                             | List all trips                           | `200`   | — |
| `POST`   | `/api/v1/trips`                             | Create a trip                            | `201`   | `400` |
| `GET`    | `/api/v1/trips/<trip_id>`                   | Get one trip (with travelers)            | `200`   | `404` |
| `PUT`    | `/api/v1/trips/<trip_id>`                   | Partially update a trip                  | `200`   | `400`, `404`, `409` |
| `DELETE` | `/api/v1/trips/<trip_id>`                   | Delete a trip                            | `200`   | `404`, `409` |
| `POST`   | `/api/v1/trips/<trip_id>/travelers`         | Add a traveler to a trip                 | `201`   | `400`, `404`, `409` |
| `DELETE` | `/api/v1/trips/<trip_id>/travelers/<traveler_id>` | Remove a traveler from a trip      | `200`   | `404` |
| `POST`   | `/api/v1/trips/<trip_id>/expenses`          | Add an expense to a trip                 | `201`   | `400`, `404`, `409` |
| `PATCH`  | `/api/v1/trips/<trip_id>/status`            | Change trip status                       | `200`   | `400`, `404`, `409` |
| `GET`    | `/api/v1/trips/<trip_id>/summary`           | Seats, expense total, remaining budget   | `200`   | `404` |

Errors are returned as JSON with a stable machine-readable `error` code and a
human-readable `message`, e.g.:

```json
{ "error": "MISSING_FIELDS", "message": "Missing required fields: budget" }
```

Routes that do not exist return `404` with `{"error": "INVALID_ROUTE", ...}`, and
using the wrong HTTP method returns `405` with `{"error": "INVALID_METHOD", ...}`.

## Example requests & responses

### Create a trip

```bash
curl -X POST http://localhost:5000/api/v1/trips \
  -H "Content-Type: application/json" \
  -d '{
        "destination": "Cox'"'"'s Bazar",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5
      }'
```

`201 Created`

```json
{
  "id": 1,
  "destination": "Cox's Bazar",
  "start_date": "2026-10-20",
  "end_date": "2026-10-23",
  "budget": 30000.0,
  "max_travelers": 5,
  "status": "PLANNED"
}
```

### Add a traveler (optionally select fields)

```bash
curl -X POST http://localhost:5000/api/v1/trips/1/travelers \
  -H "Content-Type: application/json" \
  -d '{"name": "Tini", "email": "tini@plan.com"}'
```

`201 Created`

```json
{
  "id": 1,
  "destination": "Cox's Bazar",
  "start_date": "2026-10-20",
  "end_date": "2026-10-23",
  "budget": 30000.0,
  "max_travelers": 5,
  "status": "PLANNED",
  "travelers": [
    { "id": 1, "name": "Tini", "email": "tini@plan.com" }
  ]
}
```

Adding the same traveler again:

`409 Conflict`

```json
{ "error": "TRAVELER_ALREADY_IN_TRIP", "message": "Cannot add the same traveler to a trip twice" }
```

### Update a trip

```bash
curl -X PUT http://localhost:5000/api/v1/trips/1 \
  -H "Content-Type: application/json" \
  -d '{"budget": 45000, "max_travelers": 6}'
```

`200 OK` — returns the updated trip (including `travelers`).

### Change status

```bash
curl -X PATCH http://localhost:5000/api/v1/trips/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "ongoing"}'
```

`200 OK` returns the trip with `"status": "ONGOING"`. An illegal transition
returns `409`:

```json
{ "error": "INVALID_STATUS_TRANSITION", "message": "cannot set status from PLANNED to COMPLETED" }
```

### Add an expense

```bash
curl -X POST http://localhost:5000/api/v1/trips/1/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Bus fare", "amount": 5000}'
```

`201 Created`

```json
{ "id": 1, "title": "Bus fare", "trip_id": 1, "amount": 5000.0 }
```

Spending past the remaining budget returns `409`:

```json
{ "error": "EXPENSE_EXCEEDS_BUDGET", "message": "expense cannot be larger than remaining budget, your remaining budget is 0.0" }
```

### Trip summary

```bash
curl http://localhost:5000/api/v1/trips/1/summary
```

`200 OK`

```json
{
  "traveler_count": 1,
  "available_seats": 4,
  "total_expense": 5000.0,
  "remaining_budget": 25000.0
}
```

### Health check

```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

## Business rules & assumptions

**Trips**

- Required on create: `destination`, `start_date`, `end_date`, `budget`,
  `max_travelers`. Extra fields (including `status`) are ignored — a new trip is
  always created as `PLANNED`.
- `destination` is trimmed and limited to 120 characters.
- Dates must be `YYYY-MM-DD` and valid; `end_date` must be on/after `start_date`.
- `budget` must be a positive number; `max_travelers` must be a positive integer.
- `PUT /trips/<id>` only accepts `destination`, `start_date`, `end_date`,
  `budget`, `max_travelers`. An empty/unknown body returns `400 NO_VALID_UPDATE`.
- A `COMPLETED` or `CANCELLED` trip cannot be updated (`409`).
- An `ONGOING` trip cannot be deleted (`409`).

**Status lifecycle** (`PATCH /trips/<id>/status`; accepted case-insensitively)

```
PLANNED ──▶ ONGOING ──▶ COMPLETED
   │           │
   └───────────┴──▶ CANCELLED
```

- `COMPLETED` and `CANCELLED` are terminal.
- Setting a trip to its current status is a no-op and returns `200`.
- Any other transition is rejected with `409 INVALID_STATUS_TRANSITION`.

**Travelers**

- Required: `name`, `email`. Email must be a valid address and is unique
  globally across all trips.
- If the email already exists, the supplied `name` must match the existing one,
  otherwise `409 TRAVELER_EMAIL_CONFLICT`.
- A traveler can only join a trip while it is `PLANNED` (`409 TRIP_NOT_PLANNED`).
- A traveler cannot be on two trips whose date ranges overlap
  (`409 TRAVELER_TRIP_OVERLAP`). Cancelled trips are ignored for this check.
- A trip cannot exceed `max_travelers` (`409 TRIP_FULL`).
- Removing a traveler from their last trip also deletes the traveler record.

**Budget & expenses**

- Expenses require `title` and a positive `amount`.
- Expenses can only be added while a trip is `PLANNED` or `ONGOING`
  (`409 INVALID_TRIP_STATE`).
- Total expenses may not exceed the budget (`409 EXPENSE_EXCEEDS_BUDGET`).
- `max_travelers` cannot be lowered below the number of travelers already
  assigned (`409 MAX_TRAVELERS_BELOW_CURRENT`).
- `budget` cannot be lowered below the current total expenses
  (`409 INVALID_BUDGET_AMOUNT`).
- When trip dates are updated, the change is rejected if it would make any
  assigned traveler overlap with their other trips
  (`409 DATE_CONFLICT_WITH_TRAVELERS`); the transaction is rolled back.
- Money is stored as a SQLite `REAL` (float) and rounded to 6 decimals when
  totals are compared.

The same core invariants are also enforced at the database level via
`CHECK` constraints (`end_date >= start_date`, `max_travelers > 0`,
`budget > 0`) and foreign keys.

## Project structure

```
.
├── app/
│   ├── __init__.py       # create_app() factory, DB init, /health, 404 & 405 handlers
│   ├── models.py         # SQLAlchemy models (Trip, Traveler, TripTraveler, Expense) + TripStatus enum
│   ├── routes.py         # /api/v1 blueprint: HTTP routes -> service calls
│   ├── services.py       # business logic / orchestration, returns (jsonify, status)
│   └── validations.py    # request validation + error responses used by services
├── instance/             # SQLite database file lives here (gitignored)
│   └── trip_planner.db
├── .env                  # local secrets/config (gitignored)
├── .env.example          # committed template for .env
├── .gitignore
├── requirements.txt      # Python dependencies
├── run.py                # entry point: create_app() and app.run()
├── run.sh                # bootstrap + test + run script
└── test.py               # pytest suite (in-memory SQLite)
```

Layers: 

**routes → services → validations , models**. Routes stay thin; all
business rules and validation live in the service/validation and model layer.

## How SQLite is initialized & stored

- On startup, `create_app()` resolves the database path as
  `instance/<DATABASE_NAME>` (default `trip_planner.db`) and configures
  `SQLALCHEMY_DATABASE_URI` as `sqlite:///<that path>`.
- Inside an app context it calls `db.create_all()`, which creates any missing
  tables. **There are no migrations** — this only creates tables that do not
  already exist.
- The `instance/` folder and all `*.db` files are gitignored, so each checkout
  starts with an empty database that is created on first run.
- Foreign key enforcement is enabled per connection with
  `PRAGMA foreign_keys=ON`.
- Tests bypass the file entirely: the test fixture overrides the URI with
  `sqlite:///:memory:` for an isolated, throwaway database.
- To reset the local database, stop the server and delete
  `instance/trip_planner.db`; it will be recreated on the next start.

## Known limitations

- **No authentication or authorization** — every endpoint is public.
- **No migrations** (Alembic/Flask-Migrate) — changing the schema requires
  deleting the SQLite file or managing it manually.
- **SQLite only** — a single local file, not intended for concurrent,
  high-write production workloads.
- **No pagination or filtering** on `GET /api/v1/trips`; it returns everything.
- **Expenses are append-only** — there is no endpoint to list, edit, or delete
  expenses, and `GET /trips/<id>` does not include them.

