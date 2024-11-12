from fastapi import APIRouter, HTTPException, Header, Body
from pydantic import BaseModel, Field
from auth_utils import decode_token
from mongo_conn import db
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

@router.get(
    "/relatorio",
    summary="Get user report",
    description="Retrieve a report of user activities for the past week, including total time and number of correct answers.",
    response_description="The user report.",
    responses={
        401: {"description": "Invalid or expired token"},
        404: {"description": "No activities found for the user"}
    }
)
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
    atividade_id: str = Field(..., example="60c72b2f9b1e8b3f4c8b4567")
    answer: dict = Field(..., example={"question1": "answer1"})
    time: float = Field(..., example=120.5)

@router.post(
    "/entrega",
    summary="Submit an activity delivery",
    description="Submit an activity delivery with the activity ID, answer, and time taken.",
    response_description="The delivery has been successfully submitted.",
    responses={
        400: {"description": "Invalid atividade_id format"},
        401: {"description": "Invalid or expired token"},
        404: {"description": "Activity not found"}
    }
)
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

@router.get("/atividades")
async def get_atividades():
    atividades = list(db.atividade.find({}))
    for atividade in atividades:
        atividade['_id'] = str(atividade['_id'])
    return atividades