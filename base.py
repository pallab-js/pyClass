from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For this example, we use a local SQLite database.
# The file will be created in the project's root directory.
DATABASE_URL = "sqlite:///classroom_clone.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()