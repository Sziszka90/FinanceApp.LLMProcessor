from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: Exception):
  match exc:
    case HTTPException() as http_exc:
      if getattr(http_exc, 'status_code', None) == 401:
        return JSONResponse(
          status_code=401,
          content={"detail": "Unauthorized"}
        )
      return JSONResponse(
        status_code=getattr(http_exc, 'status_code', 404),
        content={"detail": getattr(http_exc, 'detail', 'Not found')}
      )
    case ValueError():
      return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input"}
      )
    case Exception():
      return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
      )
