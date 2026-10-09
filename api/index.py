from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel
import math

app = FastAPI()


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"

    requested_headers = request.headers.get(
        "access-control-request-headers"
    )
    response.headers["Access-Control-Allow-Headers"] = (
        requested_headers or "*"
    )
    response.headers["Access-Control-Max-Age"] = "600"

    return response
