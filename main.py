from fastapi import FastAPI

from routers.user_routes import router as user_router
from routers.atividades_routes import router as atividades_router

app = FastAPI(
    title="Leiturela API",
    description="API para gerenciamento de histórias e atividades",
    version="1.0.0",
    contact={
        "name": "Pedro Victor Alexandre Ferreira Santos",
        "url": "https://www.linkedin.com/in/ferreira-pedro/",
        "email": "pedro48victor@gmail.com",
    },
)

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(atividades_router, prefix="/atividade", tags=["atividades"])
#app.include_router(dev_router, prefix="/dev", tags=["dev"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)