from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import auth_routes, event_routes 

app = FastAPI(title="NeoFi Event Management API")
@app.get("/")
def read_root():
    return {"message": "Welcoming you to the NeoFi API"}
# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)  #creation of defined tables

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(event_routes.router, prefix="/api/events", tags=["Events"])