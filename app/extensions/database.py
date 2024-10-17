from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example SQLserver
# engine = create_engine("mssql+pymssql://sa:123sabilOKE**@192.168.77.12:1433/DEMO", pool_size=0, max_overflow=0)

# SQLite
engine = create_engine("sqlite:///project.db")
Session = sessionmaker(bind=engine)
db = Session()

# Postgres
engine_postgres = create_engine("postgresql+psycopg2://postgres:postgres@192.168.77.12:5442/poweruploader", pool_size=0, max_overflow=0)
SessionPostgres = sessionmaker(bind=engine_postgres)
postgres_db = SessionPostgres()