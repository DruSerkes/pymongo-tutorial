from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo.errors import DuplicateKeyError

from models import Book, BookUpdate

router = APIRouter()


@router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    try:
        new_book = request.app.database["books"].insert_one(book)
        created_book = request.app.database["books"].find_one(
            {"_id": new_book.inserted_id}
        )
        return created_book
    except DuplicateKeyError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Duplicate key error - book already exists")


@router.get("/", response_description="List all books", status_code=status.HTTP_200_OK, response_model=List[Book])
def list_books(request: Request):
    books = list(request.app.database["books"].find(limit=100))
    return books


@router.get("/{id}", response_description="Get a single book by id", status_code=status.HTTP_200_OK, response_model=Book)
def find_book(id: str, request: Request):
    book = request.app.database["books"].find_one({"_id": id})
    if book:
        return book
    raise HTTPException(status.HTTP_404_NOT_FOUND,
                        f"book with id: {id} not found")


@router.put("/{id}", response_description="Update a book", status_code=status.HTTP_202_ACCEPTED, response_model=Book)
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book = {k: v for k, v in book.dict().items() if v is not None}
    if len(book) >= 1:
        update_result = request.app.database["books"].update_one(
            {"_id": id}, {"$set": book}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

    if (existing_book := request.app.database["books"].find_one({"_id": id})) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Book with ID {id} not found")


@router.delete("/{id}", response_description="Delete a book")
def delete_book(id: str, request: Request, response: Response):
    result = request.app.database["books"].delete_one({"_id": id})

    if result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status.HTTP_404_NOT_FOUND,
                        detail=f"Book with id {id} not found")
