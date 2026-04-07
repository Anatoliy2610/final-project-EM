import logging

from dotenv import load_dotenv

# import os
from starlette.templating import Jinja2Templates

from app.core.database import async_session_maker


load_dotenv()
# SECRET_KEY_TOKEN = os.getenv("SECRET_KEY_TOKEN")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY_TOKEN = "SECRET_KEY_TOKEN-123-321-098-890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


async def get_db():
    async with async_session_maker() as session:
        yield session
