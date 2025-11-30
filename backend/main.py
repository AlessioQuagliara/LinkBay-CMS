import uvicorn
from typing import Union
from fastapi import FastAPI

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run(host="127.0.0.1", port=8000)