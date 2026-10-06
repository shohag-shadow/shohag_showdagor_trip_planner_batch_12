from app import create_app
from dotenv import load_dotenv
from os import environ
from models
load_dotenv()
app=create_app()

if __name__=="__main__":
    app.run(port=environ.get("PORT"),debug=environ.get("FLASK_DEBUG"))