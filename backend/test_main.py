import pytest
from fastapi.testclient import TestClient
from main import app

# le client doit etre utilise comme context manager pour
# que le lifespan se declenche (init db + chargement des films)
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# test basique du healthcheck
def test_hello(client):
    resp = client.get("/hello")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mode"] in ("tmdb", "mock")
    assert data["films_en_db"] > 0  # la db doit etre chargee au demarrage

def test_movies_returns_list(client):
    resp = client.get("/movies?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 3

def test_movies_default(client):
    """verifie que par defaut on a 20 films"""
    resp = client.get("/movies")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 20

def test_movies_have_id(client):
    resp = client.get("/movies?limit=1")
    data = resp.json()
    assert "id" in data[0]

# test du detail d'un film (inception)
def test_movie_detail(client):
    resp = client.get("/movie/27205")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Inception"
    assert "cast" in data
    assert "trailer_key" in data

def test_movie_not_found(client):
    resp = client.get("/movie/999999999")
    assert resp.status_code == 200
    assert "error" in resp.json()

def test_search(client):
    resp = client.get("/search?q=nolan")
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_no_results(client):
    resp = client.get("/search?q=xyznonexistent")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 0
