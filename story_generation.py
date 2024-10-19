from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json, os
from dotenv import load_dotenv


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
def generate_stories(user_prompt):
  sys_template_str = """
    Crie uma história infantil com início meio e fim sobre {tema}. Essa história deve ter no máximo 100 palavras.
    A história pode ter como temas: amizade, fraternidade, humildade, companheirismo ou família.
    A história deve conter pelo menos 1 personagem, e se passar em algum local.
    Os textos não podem conter palavras rebuscadas ou que sejam muito cultas.
    A HISTÓRIA NÃO PODE CONTER CONTEÚDO IMPRÓPRIO PARA CRIANÇAS.

    Exemplo:
    {{
      "história": "COLOQUE O TEXTO AQUI",
    }}
    Output:"""

  human_template_str = "" #"{prompt_usuario}"

  prompt = PromptTemplate.from_template(template.format(system_prompt = sys_template_str, user_prompt = human_template_str))

  session = prompt | llm

  return session.invoke({"tema" : user_prompt})

def generate_story_chunks(user_prompt):
  sys_template_str = """
  Crie 10 textos de no máximo 30 palavras, que conte toda esta história que será indicada pelo usuário, adicionando mais elementos e informações na história.
  Cada um desses 10 textos, deve seguir a ordem de eventos abordada neste texto base. Você pode inserir mais informações em cada um desses textos, desde que siga a história que o usuário indicará.
  Seja criativo ao inserir novos elementos na história.
  Os textos não podem conter linguagem imprópria para crianças.
  Os textos não podem conter palavras rebuscadas ou que sejam muito cultas.

  Exemplo:
  {{
    "texto_1": "COLOQUE O TEXTO 1 AQUI",
    "texto_2": "COLOQUE O TEXTO 2 AQUI",
      ...
    "texto_N": "COLOQUE O TEXTO N AQUI",
  }}
  Output:"""

  human_template_str = "{prompt_usuario}"

  prompt = PromptTemplate.from_template(template.format(system_prompt = sys_template_str, user_prompt = human_template_str))

  session = prompt | llm

  return session.invoke({"prompt_usuario" : user_prompt})

def story_to_dict(story):
  story = story[8:len(story)-3]
  story_dict = json.loads(story)

  return story_dict