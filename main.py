from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import dotenv_values
from pymongo import MongoClient
from book_routes import router as book_router
from fastapi import status

config = dotenv_values(".env")

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/", status_code=status.HTTP_302_FOUND, description="Redirects to auto-generated swagger docs for the book API at /docs")
async def root():
    return RedirectResponse("/docs")

app.include_router(book_router, tags=["books"], prefix="/book")
