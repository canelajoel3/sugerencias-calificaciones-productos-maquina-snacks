from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import admin, clientes, auth
from database import Base, engine
import os
from dotenv import load_dotenv


Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(
    title= "Sistema de Feedback - Vending Machines",
    description= "API para registrar sugerencias y calificaciones mediante código QR",
    version= "1.0"
) 

raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")
origins = raw_origins.split(",")

if not os.path.exists("static"):
    os.makedirs("static/img")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(clientes.router)
app.include_router(admin.router)
app.include_router(auth.router)

RUTA_ACTUAl = os.path.dirname(os.path.abspath(__file__))
RUTA_TEMPLATES2 = os.path.join(RUTA_ACTUAl, "templates")

templates = Jinja2Templates(directory=RUTA_TEMPLATES2)


@app.get("/")
def ruta_inicio():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse, tags=["Vista Web"])
async def vista_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/registro", response_class=HTMLResponse, tags=["vista Web"])
async def vista_registro(request: Request):
    return templates.TemplateResponse(request=request, name="registro.html")
    

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)