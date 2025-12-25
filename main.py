from fastapi import FastAPI, HTTPException, Depends 
from typing import Optional 
from pydantic import BaseModel

app = FastAPI(title="ToDoList", version='0.0.1')

todos = [
  {
    "id": 1,
    "title": "todo1",
    "completed": False
  },
  {
    "id": 2,
    "title": "todo2",
    "completed": False
  },
  {
    "id": 3,
    "title": "todo3",
    "completed": False
  },
  {
    "id": 4,
    "title": "todo4",
    "completed": False
  },
  {
    "id": 5,
    "title": "todo5",
    "completed": False
  },
  {
    "id": 6,
    "title": "todo6",
    "completed": False
  },
  {
    "id": 7,
    "title": "todo7",
    "completed": False
  },
  {
    "id": 8,
    "title": "todo8",
    "completed": False
  },
  {
    "id": 9,
    "title": "todo9",
    "completed": False
  },
  {
    "id": 10,
    "title": "todo10",
    "completed": False
  },
  {
    "id": 11,
    "title": "todo11",
    "completed": False
  },
  {
    "id": 12,
    "title": "todo12",
    "completed": False
  },
  {
    "id": 13,
    "title": "todo13",
    "completed": False
  },
  {
    "id": 14,
    "title": "todo14",
    "completed": False
  },
  {
    "id": 15,
    "title": "todo15",
    "completed": False
  },
  {
    "id": 16,
    "title": "todo16",
    "completed": False
  }
]

def get_todo_storage():
    return todos

def delete_storage(idx):
    if idx < len(todos):
        todos.pop(idx)

def update_storage(idx, todo_id, new_todo):
    if idx < len(todos):
        new_todo["id"] = todo_id
        todos[idx] = new_todo

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
    todo: ToDoCreate, 
    storage=Depends(get_todo_storage)
):
    """
    create a new todo list
    """
    new_todo = {
        "id": len(storage)+ 1, 
        "title": todo.title, 
        "completed": False
    }

    storage.append(new_todo)

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
    todo_id: int,
    storage=Depends(get_todo_storage)
):
    """
    get todo by its id
    """
    for todo in storage:
        if todo["id"] == todo_id:
            return todo 
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
