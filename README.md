# Rental Property API

A Rest api built to manage trips,only a rest api.

Built with python and flask

## Requirements

- python3

## Project layout

```
.
├── app/                    # Flask app configuration and factory
│   ├── __init__.py         # create_app() factory, blueprint registration
│   ├── models.py           # SQLAlchemy models + enums + db
│   ├── routes.py           # blueprint creation for api/v1
│   ├── services.py         # service layer containing business logic
│   └── validation.py       # validation layer used by service layer
├── instance/               # SQLite DB file (gitignored)
│   └── myprojects.db
├── .env                    # Local secrets (gitignored)
├── .env.example            # Template committed to repo
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── run.sh                  # Shell script to setup and run the project
└── run.py                  # Entry point: app.run()
```


## Running the Project

Run the commands from the **project root directory**.

**Linux / macOS:**

```bash
./run.sh
```

## API documentation
todo: add api documentation 