import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from chat_endpoints.router import router as chat_router
from errors.handlers import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from server.middlewares.request_id import RequestIDMiddleware

app = FastAPI()

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(RequestValidationError)(validation_exception_handler)
app.exception_handler(Exception)(generic_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)