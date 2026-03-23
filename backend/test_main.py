from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# test basique du healthcheck
def test_hello():
    resp = client.get("/hello")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mode"] in ("tmdb", "mock")

def test_movies_returns_list():
    resp = client.get("/movies?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 3

def test_movies_default():
    """verifie que par defaut on a 20 films"""
    resp = client.get("/movies")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 20

def test_movies_have_id():
    resp = client.get("/movies?limit=1")
    data = resp.json()
    assert "id" in data[0]

# test du detail d'un film (inception)
def test_movie_detail():
    resp = client.get("/movie/27205")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Inception"
    assert "cast" in data
    assert "trailer_key" in data

def test_movie_not_found():
    resp = client.get("/movie/999999999")
    assert resp.status_code == 200
    assert "error" in resp.json()

def test_search():
    resp = client.get("/search?q=nolan")
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_no_results():
    resp = client.get("/search?q=xyznonexistent")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 0
