import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("Database URL not set in .env")

engine = create_engine(db_url)

# Starting a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Handing session to a route, guarantees cleanup
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Creating Base class
class Base(DeclarativeBase):
    pass
