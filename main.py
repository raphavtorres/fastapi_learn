import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response, Depends, HTTPException, Query
from sqlmodel import Session, select  # query and insert data in db
import requests

from models import Book
from database import BookModel, engine

app = FastAPI()

data = []


@app.on_event('startup')
async def startup_event():
    DATAFILE = pathlib.Path() / 'data' / 'books.json'
    session = Session(engine)  # responsable for sanding data to database

    # check db population
    statement = select(BookModel)
    result = session.exec(statement).first()  # getting the first row from query

    # if no results populate db with data in json
    if result is None:
        with open(DATAFILE, 'r') as file:
            books = json.load(file)
            for book in books:
                session.add(BookModel(**book))
        session.commit()

    session.close()


def get_session():
    with Session(engine) as session:
        yield session


# GET ALL BOOKS
@app.get('/api/v1/books/', response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):  # passing session dependency
    # with Session(engine) as session:  # context manager (don't need to manually close the session)
    statement = select(BookModel)
    result = session.exec(statement).all()
    return result


# GET BOOK BY ID
@app.get('/api/v1/books/{book_id}/', response_model=Union[Book, str])
def books(book_id: int, response: Response, session: Session = Depends(get_session)):
    # find book by id or return None
    book = session.get(BookModel, book_id)
    if book is None:
        response.status_code = 404
        return "Book not found"
    return book


# CREATE NEW BOOK
@app.post('/api/v1/books/', response_model=Book, status_code=201)
def add_book(book: BookModel, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    # get the id from the db after the object has been created
    session.refresh(book)
    return book


# MODIFY BOOK
@app.put('/api/v1/books/{book_id}/', response_model=Union[Book, str])
def books(book_id: int, updated_book: Book, response: Response, session: Session = Depends(get_session)):
    book = session.get(BookModel, book_id)

    if book is None:
        response.status_code = 404
        return "Book not found"

    # exclude_unset -> exclude id so it doesn't change
    book_dict = updated_book.dict(exclude_unset=True)
    for key, value in book_dict.items():
        setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


# DELETE BOOK
@app.delete('/api/v1/books/{book_id}/')
def del_book(book_id: int, response: Response, session: Session = Depends(get_session)):
    book = session.get(BookModel, book_id)

    if book is None:
        response.status_code = 404
        return "Book not found"

    session.delete(book)
    session.commit()

    return Response(status_code=200)


# GET BOOK FROM OTHER API
@app.get('/api/v1/apigoogle/{genre}/', response_model=list)
def get_api_google(genre: str):
    """
    making a request to the Google API
    EX: api/v1/apigoogle/recipe/
    """
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={genre}&filter=free-ebooks&key=AIzaSyBpFzGiGUPBBVDmiFLdEfNqIPWEpPhrOCA")
    response.raise_for_status()
    items = []
    titles = []
    for i in response.json()['items']:
        items.append(i['volumeInfo'])
    print(items)

    for i in items:
        titles.append(i['title'])
    return titles
