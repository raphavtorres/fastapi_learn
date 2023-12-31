import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response

from models import Book

app = FastAPI()

data = []


@app.on_event('startup')
async def startup_event():
    datapath = pathlib.Path() / 'data' / 'books.json'
    with open(datapath, 'r') as f:
        books = json.load(f)
        for book in books:
            data.append(Book(**book).model_dump())


# GET ALL BOOKS
@app.get('/api/v1/books/', response_model=List[Book])
def get_all_books():
    return data


# GET BOOK BY ID
@app.get('/api/v1/books/{book_id}/', response_model=Union[Book, str])
def books(book_id: int, response: Response):
    # find book by id or return None
    book = None
    for b in data:
        if b['id'] == book_id:
            book = b
            break

    if book is None:
        response.status_code = 404
        return "Book not found"
    return book


# CREATE NEW BOOK
@app.post('/api/v1/books/', response_model=Book, status_code=201)
def add_book(book: Book):
    book_dict = book.model_dump()
    # create id to new data
    book_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1
    data.append(book_dict)
    return book_dict


# MODIFY BOOK
@app.put('/api/v1/books/{book_id}/', response_model=Union[Book, str])
def books(book_id: int, updated_book: Book, response: Response):
    book = None
    for b in data:
        if b['id'] == book_id:
            book = b
            break

    if book is None:
        response.status_code = 404
        return "Book not found"

    for key, value in updated_book.model_dump().items():
        if key != 'id':  # to not change the id
            book[key] = value
    return book


# DELETE BOOK
@app.delete('/api/v1/books/{book_id}/')
def del_book(book_id: int, response: Response):
    book_index = None
    for i, b in enumerate(data):
        # fiding the object index
        if b['id'] == book_id:
            book_index = i
            break

    if book_index is None:
        response.status_code = 404
        return "Book not found"

    del data[book_index]
    return Response(status_code=200)
