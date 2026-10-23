import logging

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
  match exc:
    case HTTPException() as http_exc:
      return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": "Unauthorized" if http_exc.status_code == 401 else http_exc.detail},
      )
    case Exception():
      logger.exception("Unhandled application error for %s %s", request.method, request.url.path)
      return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
      )
