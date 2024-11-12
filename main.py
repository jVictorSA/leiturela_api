from fastapi import FastAPI, HTTPException, Body, status, Header
from typing import Union, Any, List
import os, json
from pydantic import BaseModel
from auth_utils import get_password_hash, verify_password, create_access_token, decode_token
from datetime import datetime
from bson import ObjectId

# from fastapi.responses import 
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from story_generation import generate_stories, generate_story_chunks, story_to_dict
from mongo_conn import db
from models import Story, UpdateStoryModel
from pymongo import ReturnDocument
from datetime import timedelta

from routers.user_routes import router as user_router
from routers.atividades_routes import router as atividades_router
from routers.dev_routes import router as dev_router

app = FastAPI(
    title="Leiturela API",
    description="API para gerenciamento de histórias e atividades",
    version="1.0.0",
    contact={
        "name": "Seu Nome",
        "url": "https://seusite.com",
        "email": "seuemail@exemplo.com",
    },
)

@app.get(
    "/stories/",
    response_description="List all Stories in the database",
)
async def get_stories():
    """
    List all the stories data in the database.    
    """
    stories = list(db.story.find({}))

    if stories is not None:
        for story in stories:
            story["_id"] = str(story["_id"])
    # print(stories)
        return stories
    raise HTTPException(status_code=404, detail=f"There is no record in the database")

@app.get(
    "/stories/{id}",
    response_description="List Story by Id in the database",
)
async def get_story_by_id(id: int):
    """
    List a single story by its ID.
    """
    story = await db.story.find_one({"story_id": id})
    if story is not None:
        story["_id"] = str(story["_id"])
        return story
    raise HTTPException(status_code=404, detail=f"Story {id} not found")

@app.post(
    "/stories/",
    response_description="Insert a Story in the database given a text prompt"
)
async def generate_story(story_prompt:str):
    """
    Insert a single Story record in the database given a text prompt.
    """
    base_story = generate_stories(story_prompt)    
    historia = story_to_dict(base_story.content)
    response = generate_story_chunks(historia['história'])
    response = story_to_dict(response.content)
    
    existing_story = db.story.find_one({"story_prompt": story_prompt})
    if existing_story:
        raise HTTPException(
            status_code=404, detail="História já existe no banco!!!"
        )
 
    story_id = db.story.count_documents({}) + 1
    created_story = Story.create_story(story_id, story_prompt, historia, response)

    result = db.story.insert_one(created_story.dict())
    inserted_story = db.story.find_one({"story_prompt": story_prompt})
    # print(inserted_story)
    inserted_story = str(inserted_story['story_prompt'])
    content_response = {"message": f"Story with prompt '{inserted_story}' has been created."}
    return JSONResponse(
                    content=content_response,
                    status_code=status.HTTP_201_CREATED,
                    media_type="application/json"
                )


@app.put(
    "/stories/{story_id}",
    response_description="Update a Story in the database"
)
async def update_story(story_id: int, story: UpdateStoryModel = Body(...)):
    """
    Update a single Story record from the database.
    """
    story = {
        k: v for k,v in story.model_dump(by_alias=True).items() if v is not None
    }
    
    if len(story) >= 1:
        update_result = db.story.update_one(
            {"story_id": story_id},
            {"$set": story},            
        )        

        if update_result is not None:            
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=404, detail=f"Story {story_id} not found")
    
    # The update is empty, but we should still return the matching document:
    if (existing_story := await db.story.find_one({"story_id": story_id})) is not None:
        return existing_story
    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.delete(
    "/stories/{story_id}",
    response_description="Delete a Story in the database"
)
async def delete_student(story_id: int):
    """
    Remove a single Story record from the database.
    """
    delete_result = db.story.delete_one({"story_id": story_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(atividades_router, prefix="/atividade", tags=["atividades"])
app.include_router(dev_router, prefix="/dev", tags=["dev"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)