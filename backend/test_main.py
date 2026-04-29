import pytest
from fastapi.testclient import TestClient
from main import app


# Important : TestClient en context manager pour que le lifespan
# se déclenche (init BDD + premier chargement des films).
# Sans le `with`, la BDD reste vide et tous les tests pètent.
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_hello(client):
    resp = client.get("/hello")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mode"] in ("tmdb", "mock")
    assert data["films_en_db"] > 0


def test_movies_returns_list(client):
    resp = client.get("/movies?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_movies_default(client):
    # par défaut on doit avoir 20 films
    resp = client.get("/movies")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 20


def test_movies_have_id(client):
    resp = client.get("/movies?limit=1")
    data = resp.json()
    assert "id" in data[0]


def test_movie_detail(client):
    # 27205 = Inception (présent dans nos mocks ET dispo sur TMDB)
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


# --- exports (TME 3) ---

def test_export_json(client):
    resp = client.get("/export/movies.json")
    assert resp.status_code == 200
    assert "attachment" in resp.headers.get("content-disposition", "")
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]


def test_export_csv(client):
    resp = client.get("/export/movies.csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    text = resp.text
    first_line = text.split("\n")[0]
    assert "title" in first_line
    assert "director" in first_line


# --- pagination (TME §7) ---

def test_movies_paginated_format(client):
    # Quand "page" est passe, on doit recevoir un dict avec items + meta.
    resp = client.get("/movies?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "page" in data
    assert "total_pages" in data
    assert len(data["items"]) <= 5
    assert data["page"] == 1


def test_movies_paginated_page2(client):
    # On doit pouvoir aller chercher la page 2.
    resp = client.get("/movies?page=2&page_size=5")
    assert resp.status_code == 200
    assert resp.json()["page"] == 2


# --- recommandations (TME §7) ---

def test_similar_movies(client):
    resp = client.get("/movie/27205/similar")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


# --- /status ---

def test_status(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "running"
    assert data["mode"] in ("tmdb", "mock")
    assert data["films_en_db"] > 0
    assert "uptime" in data
    assert data["uptime_seconds"] >= 0
