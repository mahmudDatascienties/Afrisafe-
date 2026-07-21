from app.database.database import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

from app.routes.auth import router as auth_router

app.include_router(auth_router)

from app.database import Base
from app.database import engine

import app.models.user

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    ml_service.load_model()

    yield
