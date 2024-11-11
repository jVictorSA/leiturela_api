from fastapi import APIRouter, Body
from pydantic import BaseModel
from mongo_conn import db

router = APIRouter()

class AtividadePost(BaseModel):
    type: str
    answer: dict
    body: dict

@router.post("/atividade")
async def atividade(atividade: AtividadePost = Body(...)):
    nova_atividade = db.atividade.insert_one(atividade.dict())
    return {"message": "Atividade criada com sucesso", "id": str(nova_atividade.inserted_id)}