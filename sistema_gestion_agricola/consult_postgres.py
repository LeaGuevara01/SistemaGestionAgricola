import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM maquinas"))
    count = result.scalar()
    print(f"Cantidad de máquinas: {count}")
