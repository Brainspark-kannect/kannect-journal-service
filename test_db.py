from app.config.database import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {str(e)}') 