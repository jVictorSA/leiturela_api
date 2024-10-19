# leiturela_api
API em FastAPI para o Backend do app Leiturela

## Criação do Banco de Dados MongoDB
* Crie um banco de dados no MongoDB com o nome de `stories_db` em uma instância do MongoDB rodando na porta `27017`
* Entre neste banco de dados e crie um usuário com nome de `storyUser` e senha `u9zA0qr*`

## Criação do Ambiente Virtual
* `python -m venv leiturela_api_venv`

## Execução do Ambiente Virtual
* `source leiturela_api_venv/bin/activate`
* `pip install "fastapi[standard]"`
* `pip install -r requirements.txt`

## Execução da API
* Inicie o servidor: `fastapi dev main.py`
* Interaja com a documentação SwaggerUI: `http://localhost:8000/docs/`