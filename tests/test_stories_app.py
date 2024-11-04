import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)



 #---------------> Testando a listagem de todas as histórias


# def test_get_stories():
#     response = client.get("/stories/")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)



#  #---------------> Testando a obtenção de uma história por ID


# def test_get_story_by_id():
#     # Inserir uma história para o teste
#     client.post("/stories/", json={"story_prompt": "Test prompt"})
    
#     # Recuperar a história criada
#     response = client.get("/stories/6")
#     assert response.status_code == 200
#     assert "story_prompt" in response.json()

#     # Testar uma história inexistente
#     response = client.get("/stories/999")
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Story 999 not found"}



 #---------------> Testando a criação de uma nova história


# def test_create_story():
#     response = client.post("/stories/?story_prompt=Festa da Ana", json={
#         "base_story": {"história": "Base story example"},
#         "sub_stories": {"sub_story_1": "Sub story example"}
#     })
    
#     print(f"Status Code: {response.status_code}")
#     print(f"Response Content: {response.content}")
    
#     assert response.status_code == 201
#     assert "message" in response.json()
    
#     created_story_id = response.json()["story_id"]
#     return created_story_id
    
#  #---------------> Testando atualização da história
 
 
def test_update_story():
    # Criar uma nova história e obter o ID
    # created_story_id = test_create_story()
    # Atualizar a história criada
    update_data = {
        "story_prompt": "Batman e Capitão América",
        "base_story": {"história": "Base story atualizada"},
        "sub_stories": {"texto_1": "Sub story atualizada"}
    }
    update_response = client.put(f"/stories/{1}",  json={
         "base_story": {"história": "Base story example"},
         "sub_stories": {"sub_story_1": "Sub story example"}
     })

    assert update_response.status_code == 204

    # Verificar se a história foi atualizada corretamente
    get_response = client.get(f"/stories/{1}")
    assert get_response.status_code == 200
    updated_story = get_response.json()
    

 #---------------> Testando a exclusão de uma história


def test_delete_story():
    # Inserir uma história para o teste
    client.post("/stories/", json={"story_prompt": "Story to delete"})

    # Deletar a história
    response = client.delete("/stories/0")
    assert response.status_code == 204

    # Testar exclusão de uma história inexistente
    response = client.delete("/stories/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Story 999 not found"}
