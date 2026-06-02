from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base 
import os 
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

USUARIO = os.getenv("DB_USUARIO")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")

password_codificada = urllib.parse.quote_plus(PASSWORD)

CONEXION = f"mysql+pymysql://{USUARIO}:{password_codificada}@{HOST}:{PORT}/{NAME}"

engine = create_engine(url=CONEXION, echo=True)

session_base = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()



def get_db():
    db = session_base()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__": 
    try: 
        with engine.connect() as conexion:
            print("Conexion exitosa")
    except Exception as e:
        print(f"Error al conectar:\n {e}") 