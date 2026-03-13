from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./execos.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
