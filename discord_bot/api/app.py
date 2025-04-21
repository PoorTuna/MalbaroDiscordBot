import os

from fastapi import FastAPI
from starlette.templating import Jinja2Templates

app = FastAPI()
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")
templates = Jinja2Templates(directory="templates")