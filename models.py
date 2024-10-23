from typing import Union, Any, List, Optional
from pydantic import BaseModel, Json, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class Atividade(BaseModel):
    atividade_id: str
    answer: str
    body: dict

class Story(BaseModel):
    story_id: int
    story_prompt: str
    base_story: dict
    sub_stories: dict

    @classmethod
    def create_story(cls, id, story_prompt: str, base_story: Json, sub_stories: Json):
        return cls(story_id=id, story_prompt=story_prompt, base_story=base_story, sub_stories=sub_stories)

class UpdateStoryModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """    
    story_prompt: Optional[str] = None
    base_story: Optional[dict] = {}
    sub_stories: Optional[dict] = {}

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "story_prompt": "Pato Orisvaldo",
                "base_story": {"história": "O pato Orisvalo brincava nos campos"},
                "sub_stories": {"texto_1": "O pato orisvaldo brincava nos campos", "texto_2": "Orisvaldo encontrou uma"},
            }
        },
    )