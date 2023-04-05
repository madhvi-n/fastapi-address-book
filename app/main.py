import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from endpoints import address_router

app = FastAPI()
app.include_router(address_router)

origins = ["http://localhost:8005"]

APP_PORT = 8005

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=APP_PORT, log_level="info", reload=True)
    print(f"FastAPI Running on port {APP_PORT}")
