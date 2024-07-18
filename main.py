from fastapi import FastAPI
import uvicorn

from items_views import router as items_router
from users.views import router as users_router

app = FastAPI()
app.include_router(users_router)
app.include_router(items_router)


@app.get("/")
def hello_index():
    return {
        "message": "Hi, Lebovsky",
    }


@app.get("/hello/")
def hello(name: str):
    name = name.strip().title()
    return {"message": f"Hi, {name}"}


@app.post("/calc/add/")
def add(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "summ": a + b,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
