import sys
import os

# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import json
from pydantic import BaseModel
from typing import List, Dict, Optional
from mongo_conn import db
import random

load_dotenv()
os.environ["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    generation_config={"response_mime_type": "application/json"},
    stop=["<|eot_id|>"],        
)

template = """
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    {system_prompt}
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    {user_prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

def generate_story(theme: str) -> str:
    """
    Gera uma história infantil baseada no tema fornecido.
    
    Args:
        theme (str): O tema da história.
    
    Returns:
        str: A história gerada.
    """
    sys_template_str = """
    Crie uma história infantil com início, meio e fim sobre {tema}. Essa história deve ter no máximo 200 palavras.
    A história pode ter como temas: amizade, fraternidade, humildade, companheirismo ou família.
    A história deve conter pelo menos 1 personagem, e se passar em algum local.
    Os textos não podem conter palavras rebuscadas ou que sejam muito cultas.
    A HISTÓRIA NÃO PODE CONTER CONTEÚDO IMPRÓPRIO PARA CRIANÇAS.
    Output:"""

    human_template_str = ""  # "{prompt_usuario}"

    prompt = PromptTemplate.from_template(template.format(system_prompt=sys_template_str, user_prompt=human_template_str))

    session = prompt | llm

    response = session.invoke({"tema": theme})
    story = response.content.replace("\n", " ").strip()
    return story

def generate_story_chunks(story: str) -> list:
    """
    Divide a história em várias sub-histórias.
    
    Args:
        story (str): A história completa.
    
    Returns:
        list: Uma lista de sub-histórias.
    """
    sys_template_str = """
    Divida a seguinte história em 10 sub-histórias, cada uma com no máximo 50 palavras:
    {story}

    EXEMPLO: ["Texto 1", "Texto 2", "Texto 3", ...]
    Output:"""

    human_template_str = ""  # "{prompt_usuario}"

    prompt = PromptTemplate.from_template(template.format(system_prompt=sys_template_str, user_prompt=human_template_str))

    session = prompt | llm

    response = session.invoke({"story": story})
    sub_stories_str = response.content.strip()

    #remover <|file_separator|>
    sub_stories_str = sub_stories_str.replace("<|file_separator|>", "")

    # remover aspas triplas e json
    sub_stories_str = sub_stories_str.replace("```json\n", "")
    sub_stories_str = sub_stories_str.replace("```", "")
    if sub_stories_str.startswith("```") and sub_stories_str.endswith("```"):
        sub_stories_str = sub_stories_str[3:-3].strip()
        print(f"Response content after removing triple quotes: {sub_stories_str}")
    # remover a tag json
    if sub_stories_str.startswith("json\n"):
        print(f"Response content before JSON parsing: {sub_stories_str}")
        sub_stories_str = sub_stories_str[5:]

    print(f"Response content before JSON parsing: {sub_stories_str}")

    sub_stories = json.loads(sub_stories_str)
    return sub_stories

def generate_activity(sub_story: str) -> dict:
    """
    Gera uma atividade baseada na sub-história fornecida.
    
    Args:
        sub_story (str): A sub-história.
    
    Returns:
        dict: A atividade gerada.
    """

    tipos_json = [
        {"type":"conta_letra","answer":{"num":5},"body":{"letra":"A","frase":"A arara azul voa alto sobre as árvores"}},
        {"type":"desembaralha_palavra","answer":{"palavra":"casa"},"body":{"silabas":["ca","sa"]}},
    ]
    choice = random.choice(tipos_json)

    sys_template_str = """
    Crie uma atividade no formato JSON do tipo {choice} baseada, mas sem ser identica a seguinte frase:
    {sub_story}

    A atividade deve incluir uma pergunta e uma resposta correta, escolha algum dos dos tipos de exemplo abaixo.

    EXEMPLO: 
    {choice}
    Output:"""

    human_template_str = ""  # "{prompt_usuario}"

    prompt = PromptTemplate.from_template(template.format(system_prompt=sys_template_str, user_prompt=human_template_str))

    session = prompt | llm

    response = session.invoke({"sub_story": sub_story, "choice": choice})
    activity_str = response.content

    if not activity_str:
        raise ValueError("Received empty response from the model")
    
    if activity_str.startswith("```") and activity_str.endswith("```"):
        activity_str = activity_str[3:-3].strip()

    if activity_str.startswith("json\n"):
        activity_str = activity_str[5:]

    print(f"Response content before JSON parsing: {activity_str}")

    try:
        activity = json.loads(activity_str)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Response content: {activity_str}")
        raise

    if activity['type'] == 'conta_letra':
        # contar as letras da frase
        activity['answer']['num'] = activity['body']['frase'].lower().count(activity['body']['letra'].lower())

    return activity

class Atividade(BaseModel):
    type: str
    answer: Optional[dict] = None
    body: dict

class Story(BaseModel):
    story_prompt: str
    historia: str
    chunks: List[str]
    activities: List[str]  # Armazena IDs das atividades

    @classmethod
    def create_story(cls, story_prompt: str, historia: str, chunks: List[str], activities: List[Dict]):
        activity_ids = []
        for activity in activities:
            atividade = Atividade(**activity)
            result = db.activities.insert_one(atividade.dict())
            activity_ids.append(str(result.inserted_id))
        
        story_instance = cls(
            story_prompt=story_prompt,
            historia=historia,
            chunks=chunks,
            activities=activity_ids
        )
        
        # Salve a história no banco de dados
        db.stories.insert_one(story_instance.dict())
        
        return story_instance


# Exemplo de uso
if __name__ == "__main__":
    theme = input("Digite o tema da história: ")
    story = generate_story(theme)
    print("História completa:")
    print(story)
    
    sub_stories = generate_story_chunks(story)
    #atividade = [generate_activity(item) for item in sub_stories]
    atividade = []
    for item in sub_stories:
        print("Sub-história:", item)
        print("Digite o json da atividade:")
        json_str = input()
        atividade.append(json.loads(json_str))
    story_instance = Story.create_story(theme, story, sub_stories, atividade)