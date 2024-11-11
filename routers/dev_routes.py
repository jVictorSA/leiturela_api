from fastapi import APIRouter, Body
from pydantic import BaseModel
from mongo_conn import db
from bson import ObjectId
from fastapi import HTTPException
from typing import List

router = APIRouter()

class AtividadePost(BaseModel):
    type: str
    answer: dict
    body: dict

@router.post("/atividade")
async def atividade(atividade: AtividadePost = Body(...)):
    nova_atividade = db.atividade.insert_one(atividade.dict())
    return {"message": "Atividade criada com sucesso", "id": str(nova_atividade.inserted_id)}

class StoryAtividade(BaseModel):
    story_id: str
    atividades: List[str]

@router.put("/story_atividade")
async def story_atividade(story_atividade: StoryAtividade = Body(...)):
    try:
        story_obj_id = ObjectId(story_atividade.story_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid story_id format")
    
    atividades = story_atividade.atividades
    
    update_result = db.story.update_one(
        {"_id": story_obj_id},
        {"$set": {"atividades": atividades}}
    )
    
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return {"message": "Story updated successfully"}