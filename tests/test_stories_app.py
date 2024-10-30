import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)



 #---------------> Testando a listagem de todas as histórias


def test_get_stories():
    response = client.get("/stories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)



 #---------------> Testando a obtenção de uma história por ID


def test_get_story_by_id():
    # Inserir uma história para o teste
    client.post("/stories/", json={"story_prompt": "Test prompt"})
    
    # Recuperar a história criada
    response = client.get("/stories/6")
    assert response.status_code == 200
    assert "story_prompt" in response.json()

    # Testar uma história inexistente
    response = client.get("/stories/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Story 999 not found"}



 #---------------> Testando a criação de uma nova história


def test_create_story():
    response = client.post("/stories/?story_prompt=Festa da Ana", json={
        "base_story": {"história": "Base story example"},
        "sub_stories": {"sub_story_1": "Sub story example"}
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    assert response.status_code == 201
    assert "message" in response.json()
    
 #---------------> Testando atualização da história
 
 
# def test_update_story():
    
    # # Inserir uma história para o teste
    # response = client.post("/stories/?story_prompt=1234 maçã", json={
    #     "base_story": {"história": "Base story example"},
    #     "sub_stories": {"sub_story_1": "Sub story example"}
    # })
    
    # # Verificar se a história foi criada com sucesso
    # assert response.status_code == 201
    # inserted_story = response.json()  
    # story_id = inserted_story.get("story_id") 

    # # Atualizar a história
    # updated_story_prompt = "Boi"
    # response = client.put(f"/stories/{story_id}?story_prompt={updated_story_prompt}")
    
    # # Verificar se a atualização foi bem-sucedida
    # assert response.status_code == 204

    # # Confirmar que a história foi realmente atualizada
    # response_check = client.get(f"/stories/{story_id}")
    # assert response_check.status_code == 200
    # updated_story = response_check.json()
    # assert updated_story["story_prompt"] == updated_story_prompt

    # # Testar atualização de uma história inexistente
    # response = client.put("/stories/999", json={"story_prompt": "Nonexistent story"})
    # assert response.status_code == 404
    # assert response.json() == {"detail": "Story 999 not found"}



 #---------------> Testando a exclusão de uma história


def test_delete_story():
    # Inserir uma história para o teste
    client.post("/stories/", json={"story_prompt": "Story to delete"})

    # Deletar a história
    response = client.delete("/stories/6")
    assert response.status_code == 204

    # Testar exclusão de uma história inexistente
    response = client.delete("/stories/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Story 999 not found"}
