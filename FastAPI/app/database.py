from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#just copy and paste the code from the SQLAlchemy documentation, and then modify it to fit our needs.
SqlALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:52236385@localhost/Fastapi"

engine = create_engine(SqlALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()