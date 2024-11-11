from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from auth_utils import get_password_hash, verify_password, create_access_token, decode_token
from mongo_conn import db  # Supondo que você tenha um módulo db para acessar o banco de dados
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Body, status, Header
from bson import ObjectId

router = APIRouter()

@router.get("/relatorio")
async def relatorio(authorization: str = Header(...)):
    token = authorization
    payload = decode_token(token)
    user_id = payload["id"]
    # filtrar por a data de nao mais antiga que uma semana
    entregas = list(db.entrega.find({"user_id": user_id, "date": {"$gte": datetime.now() - timedelta(days=7)}}))
    # retornar a soma do tempo de cada entrega
    total_time = sum([entrega["time"] for entrega in entregas])
    # contar o número de acertos
    num_acertos = sum([1 for entrega in entregas if entrega["correta"]])
    return {"entregas": entregas, "total_time": total_time, "num_acertos": num_acertos}


class EntregaPost(BaseModel):
    atividade_id: str
    answer: dict
    time: float

@router.post("/entrega")
async def entrega(authorization: str = Header(...), entrega: EntregaPost = Body(...)):
    token = authorization 
    payload = decode_token(token)

    try:
        atividade_obj_id = ObjectId(entrega.atividade_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid atividade_id format")
    atividade = db.atividade.find_one({'_id': atividade_obj_id})
    correta = (atividade["answer"] == entrega.answer)
    # colocar o id do usuário pelo payload do jwt
    new_entrega = {
        "atividade_id": entrega.atividade_id,
        "answer": entrega.answer,
        "correta": correta,
        "date": datetime.now(),
        "user_id": payload["id"],
        "time": entrega.time
    }
    db.entrega.insert_one(new_entrega)
    return {
        "message": "Entrega realizada com sucesso", 
        "payload": payload, 
        "atividade_id": entrega.atividade_id, 
        "answer": entrega.answer
    }




class AtividadeGet(BaseModel):
    atividade_id: str

@router.get("/atividade")
async def get_atividade(atividade: AtividadeGet = Body(...)):
    try:
        atividade_obj_id = ObjectId(atividade.atividade_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid atividade_id format")
    
    atividade = db.atividade.find_one({'_id': atividade_obj_id})
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade not found")
    
    atividade['_id'] = str(atividade['_id'])
    return atividade