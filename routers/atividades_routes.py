from fastapi import APIRouter, HTTPException, Header, Body
from pydantic import BaseModel, Field
from auth_utils import decode_token
from mongo_conn import db
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Dict, Any

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
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user_id = payload["id"]
    # filtrar por a data de nao mais antiga que uma semana
    entregas = (list(db.entrega.find({"user_id": user_id, "date": {"$gte": datetime.now() - timedelta(days=7)}})))
    # retornar a soma do tempo de cada entrega
    total_time = sum([entrega["time"] for entrega in entregas])
    # contar o número de acertos
    return {"entregas": len(entregas), "total_time": total_time}

class EntregaPost(BaseModel):
    atividade_id: str = Field(..., example="60c72b2f9b1e8b3f4c8b4567")
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

    # colocar o id do usuário pelo payload do jwt
    new_entrega = {
        "atividade_id": entrega.atividade_id,
        "date": datetime.now(),
        "user_id": payload["id"],
        "time": entrega.time
    }
    db.entrega.insert_one(new_entrega)
    return {
        "message": "Entrega realizada com sucesso", 
        "atividade_id": entrega.atividade_id, 
    }

class AtividadeGet(BaseModel):
    atividade_id: str

@router.get("/atividade:{atividade_id}")
async def get_atividade(atividade_id: str):
    try:
        atividade_obj_id = ObjectId(atividade_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid atividade_id format")
    
    atividade = db.activities.find_one({'_id': atividade_obj_id})
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade not found")
    
    atividade['_id'] = str(atividade['_id'])
    return atividade

@router.get("/atividades")
async def get_atividades():
    atividades = list(db.activities.find({}))
    for atividade in atividades:
        atividade['_id'] = str(atividade['_id'])
    return atividades

@router.get("/story:{story_id}", response_model=Dict[str, Any])
async def get_story(authorization: str = Header(None), story_id: str = None):
    """
    Recupera uma história específica do banco de dados com base no `story_id` fornecido.

    Parâmetros:
    - story_id (str): O ID da história que voc�� deseja recuperar.
    - authorization (str, opcional): Token JWT necessário para autenticação. Se não for fornecido, a resposta será `401 Unauthorized`.

    Respostas:
    - 200 OK: Retorna os detalhes da história.
    - 400 Bad Request: O formato do `story_id` é inválido.
    - 401 Unauthorized: O token de autorização não foi fornecido ou é inválido.
    - 404 Not Found: A história com o `story_id` fornecido não foi encontrada.
    """
    print(authorization)
    if authorization is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization
    payload = decode_token(token)

    try:
        story_obj_id = ObjectId(story_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid story_id format")
    
    story = db.stories.find_one({'_id': story_obj_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story['_id'] = str(story['_id'])
    activities = []
    for activity_id in story["activities"]:
        activity_obj_id = ObjectId(activity_id)
        activity = db.activities.find_one({'_id': activity_obj_id})
        activity['_id'] = str(activity['_id'])
        activities.append(activity)
    story["activities"] = activities
    return story

@router.get("/stories")
async def get_stories():
    # List all the stories data in the database.
    stories = list(db.stories.find({}))
    for story in stories:
        story["_id"] = str(story["_id"])

    return stories