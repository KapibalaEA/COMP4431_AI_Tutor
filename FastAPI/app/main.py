from dbm import error
from typing import Optional
from fastapi import  Body, FastAPI, Response, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from app.database import Base ,engine, get_db
from app import models  # ensures Post is registered # ensures Post is registered
from app.search import search_topic, get_bookshelf_resources

Base.metadata.create_all(bind=engine)# create the tables in the database, if they do not exist already.

app = FastAPI()

# Allow Next.js frontend (and Vercel preview) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon: Next.js (localhost:3000 + Vercel). Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Person 3: Web Scraper Agent (bookshelf) ----
@app.get("/search")
def search(topic: str = "merge sort algorithm", max_results: int = 5):
    """Single-topic search. GET /search?topic=merge+sort&max_results=5"""
    return {"topic": topic, "results": search_topic(topic, max_results=max_results)}


@app.get("/bookshelf")
def bookshelf(topics: str = "merge sort,binary search,divide and conquer", per_topic: int = 3):
    """Resources for 3D bookshelf. GET /bookshelf?topics=topic1,topic2 or POST with JSON body."""
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    return {"resources": get_bookshelf_resources(topic_list, per_topic=per_topic)}


@app.post("/bookshelf")
def bookshelf_post(topics: list[str] = Body(..., example=["merge sort", "binary search"]), per_topic: int = 3):
    """Same as GET but topics in body. Person 2 can send extracted topics here."""
    return {"resources": get_bookshelf_resources(topics, per_topic=per_topic)}


# title string content string, we can use pydantic to create a model for the post, and then use that model to validate the data that is sent to the server. This way we can ensure that the data is in the correct format and that it contains all the required fields.
class Post(BaseModel):
    title: str = "Jane Doe"
    content: str
    published: bool = True # default value is true, if the user does not provide a value for published, it will be set to true by default.
    #rating: Optional[int] = None

while True:
    try :
        conn = psycopg2.connect(host='localhost', database='Fastapi', user='postgres',
                             password='52236385', cursor_factory=RealDictCursor)
        cursor = conn.cursor() # cursor is used to execute SQL commands and fetch data from the database. 
        print("Database connection successful")
        break
    except Exception as error:
        print("Database connection failed")
        print("Error: ",error)
        time.sleep(2)

my_posts = [{"title": "post1", "content": "content1", "published": True, "rating": 5, "id": 1},
            {"title": "post2", "content": "content2", "published": False, "rating": 4, "id": 2}]
# get method is used to read data from the server, it is the most common method used in RESTful APIs. It is used to retrieve data from the server and does not modify any data on the server. The get method is idempotent, which means that it can be called multiple times without changing the state of the server.

def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post

def find_index_post(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index

@app.get("/posts") #read
def read_root():
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    return {"data": posts}

@app.get("/sqlalchemy") #read
def test_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)#Create
#By default, FastAPI will return a 200 status code for successful requests,
#but we can specify a different status code using the status_code parameter in the decorator.
#In this case, we are specifying that the status code should be 201 Created
def create_post(new_post: Post ):
    #print(new_post)
    #print(new_post.dict())
    #new_post_dict = new_post.dict()
    #new_post_dict['id'] = randrange(0, 1000000)
    #my_posts.append(new_post_dict)
    
    new_post  = cursor.execute("INSERT INTO post (title, content, published) VALUES (%s, %s, %s)" \
    " RETURNING *", (new_post.title, new_post.content, new_post.published) )
    created_post = cursor.fetchone()
    conn.commit()#commit the changes to the database, if we do not commit the changes, they will not be saved to the database.
    return {"data": created_post}

@app.get("/posts/{id}")#get the id, Read
def getpost(id: int, response: Response): # you can also use path parameters to get the id of the post, and then use that id to find the post in the list of posts.
    # if there is a route that has a string parameter, it will catch that route instead of this one,
    # to avoid this, we can use the type hinting to specify that the id should be an integer, 
    # and then FastAPI will automatically convert the id to an integer before passing it to the function. 
    post = find_post(int(id))# it will return a string, we need to convert it to an integer
    if not post:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, 
                            detail=f"post with id {id} not found")
    #   response.status_code = status.HTTP_404_NOT_FOUND
    #   return {"message": f"post with id {id} not found"}
    return {"post details": post}


#def create_post(payload: dict = Body(...)):
#print(payload)
#     return {"message": f"title: {payload['title']} content: {payload['content']}"}

     

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    #need to be int because the id in the database is stored as an integer, 
    #and we need to match the data type of the id in the database with the data 
    # type of the item_id that we are passing to the function.
    cursor.execute("SELECT * FROM post WHERE id = %s", (str(item_id),))
    # we need to convert the item_id to a string because the id in the database is stored as a string,
    # and we need to match the data type of the id in the database with the data type of the item_id that we are passing to the function.
    return {"item_id": item_id, "q": q}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)#delete
def delete_post(id: int):
    #deleting a post
    #
    cursor.execute("DELETE FROM post WHERE id = %s RETURNING *", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, 
                            detail=f"post with id {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")#update
def update_post(id: int, post: Post):
    #index = find_index_post(id)
    #if index == None:
    #    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, 
    #                        detail=f"post with id {id} not found")
    #post_dict = post.dict()
    #post_dict['id'] = id
    #my_posts[index] = post_dict
    cursor.execute("UPDATE post SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", 
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, 
                            detail=f"post with id {id} not found")
    return {"data": updated_post}