from fastapi import FastAPI, HTTPException, Depends 
from database.connector import Connector 
from typing import Optional 
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
load_dotenv()

POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_DB_NAME=os.getenv('POSTGRES_DB_NAME')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')

conn = Connector(
  username=POSTGRES_USER, 
  database=POSTGRES_DB_NAME, 
  host=POSTGRES_HOST, 
  port=POSTGRES_PORT, 
  password=POSTGRES_PASSWORD or None
)

app = FastAPI(title="ToDoList", version='0.0.1')

def get_todo_storage():
  pass

class ToDoCreate(BaseModel):
    title: str

class ToDoUpdate(BaseModel):
    title: str 
    completed: bool

class ToDoResponse(BaseModel):
    id: int 
    title: str 
    completed: bool

@app.get("/")
async def health_check():
    return {"Working Good"}

@app.post("/todos", response_model=ToDoResponse, status_code=201)
async def createTodo(
    todo: ToDoCreate
):
    """
    create a new todo list
    """
    insert_query = """
      INSERT INTO todolist 
      (title, completed) 
      VALUES (%s, %s) 
      RETURNING id
    """

    values = (todo.title, False)
    new_id = conn.insert_query(insert_query, values)

    new_todo = {
      "id": new_id, 
      "title": todo.title, 
      "completed": False
    }

    return new_todo

@app.get("/todos", response_model=list[ToDoResponse], status_code=200)
async def getTodo(
    completed_status: Optional[bool] = None, 
    offset: int = 0, 
    limit: int = 10,
    storage=Depends(get_todo_storage)
):
    """
    return all the todos
    with 
        pagenation 
        completed status
    """
    result = []
    if completed_status is None:
        print(offset*limit, offset*limit + limit)
        for idx in range(offset*limit, offset*limit + limit):
            if idx < len(storage):
                result.append(storage[idx])
        return result
    
    for idx in range(offset*limit, offset*limit + limit):
        if idx < len(storage) and storage["completed"] == completed_status:
            result.append(storage[idx])
    return result

@app.get("/todos/{todo_id}", response_model=ToDoResponse | None, status_code=200)
async def getToDoById(
    todo_id: int
):
    try:
      """
      get todo by its id
      """
      search_query = """
        SELECT * FROM todolist
        WHERE id = %s
      """

      values = (todo_id, )

      res = conn.execute_query(search_query, values)
      #returns a list because of fetch_all
      res = res[0]
      return res
    except Exception as e:
      raise HTTPException(status_code=404, detail="id does not found")

@app.put("/todos/{todo_id}", response_model=ToDoResponse)
async def updateToDo(
    todo_id: int, 
    new_todo: ToDoUpdate, 
    storage=Depends(get_todo_storage)
):
    """
    update the todo based on its id
    """
    for idx, todo in enumerate(storage):
        if todo["id"] == todo_id:
            update_storage(idx, todo_id, dict(new_todo))
            return storage[idx] 
    raise HTTPException(status_code=404, detail=f'todo list with id: {todo_id} not found')

@app.delete("/todos/{todo_id}", status_code=204)
async def deleteToDo(
    todo_id: int, 
    storage=Depends(get_todo_storage)
):
    """
    delete todo based on id
    """
    for idx, todo in enumerate(storage):
        if todo["id"] == todo_id:
            delete_storage(idx)
            return
    raise HTTPException(status_code=404, detail=f'todo list with id: {todo_id} not found')
