import os
import json
import sqlite3
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- config ---

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"

# chemin de la base de donnees (peut etre override par variable d'env)
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "films.db"))

# intervalle de rafraichissement en secondes (1 heure)
REFRESH_INTERVAL = 3600


# --- donnees mock (fallback sans cle TMDB) ---

MOCK_MOVIES = [
    {"id": 27205, "title": "Inception", "year": "2010", "director": "Christopher Nolan",
     "description": "Un voleur s'introduit dans les rêves des autres pour voler leurs secrets les plus enfouis.",
     "image_url": "https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg",
     "genre": "Sci-Fi"},
    {"id": 157336, "title": "Interstellar", "year": "2014", "director": "Christopher Nolan",
     "description": "Des explorateurs voyagent à travers un trou de ver pour trouver un nouveau foyer pour l'humanité.",
     "image_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
     "genre": "Sci-Fi"},
    {"id": 155, "title": "The Dark Knight", "year": "2008", "director": "Christopher Nolan",
     "description": "Batman affronte le Joker, un génie du crime qui plonge Gotham dans le chaos.",
     "image_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
     "genre": "Action"},
    {"id": 496243, "title": "Parasite", "year": "2019", "director": "Bong Joon-ho",
     "description": "Une famille pauvre s'infiltre dans la vie d'une famille riche avec des conséquences inattendues.",
     "image_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
     "genre": "Thriller"},
    {"id": 438631, "title": "Dune", "year": "2021", "director": "Denis Villeneuve",
     "description": "Paul Atreides voyage vers Arrakis, la planète la plus dangereuse de l'univers.",
     "image_url": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
     "genre": "Sci-Fi"},
    {"id": 603, "title": "The Matrix", "year": "1999", "director": "Les Wachowski",
     "description": "Un hacker découvre que la réalité est une simulation créée par des machines.",
     "image_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
     "genre": "Sci-Fi"},
    {"id": 335984, "title": "Blade Runner 2049", "year": "2017", "director": "Denis Villeneuve",
     "description": "Un blade runner découvre un secret enfoui qui pourrait plonger la société dans le chaos.",
     "image_url": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
     "genre": "Sci-Fi"},
    {"id": 244786, "title": "Whiplash", "year": "2014", "director": "Damien Chazelle",
     "description": "Un jeune batteur de jazz est poussé à ses limites par un professeur tyrannique.",
     "image_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
     "genre": "Drama"},
    {"id": 530915, "title": "1917", "year": "2019", "director": "Sam Mendes",
     "description": "Deux soldats britanniques traversent le territoire ennemi pour livrer un message crucial.",
     "image_url": "https://image.tmdb.org/t/p/w500/iZf0KyrE25z1sage4SYFqfEAq5e.jpg",
     "genre": "War"},
    {"id": 475557, "title": "Joker", "year": "2019", "director": "Todd Phillips",
     "description": "Arthur Fleck, comédien raté, sombre dans la folie et devient le Joker.",
     "image_url": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
     "genre": "Drama"},
    {"id": 76341, "title": "Mad Max: Fury Road", "year": "2015", "director": "George Miller",
     "description": "Dans un désert post-apocalyptique, Max et Furiosa fuient un tyran impitoyable.",
     "image_url": "https://image.tmdb.org/t/p/w500/hA2ple9q4qnwxp3hKVNhroipsir.jpg",
     "genre": "Action"},
    {"id": 545611, "title": "Everything Everywhere All at Once", "year": "2022", "director": "Daniels",
     "description": "Une immigrée chinoise découvre qu'elle peut accéder aux vies de ses doubles dans d'autres univers.",
     "image_url": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
     "genre": "Sci-Fi"},
    {"id": 680, "title": "Pulp Fiction", "year": "1994", "director": "Quentin Tarantino",
     "description": "Les vies de truands, gangsters et petits criminels s'entremêlent à Los Angeles.",
     "image_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
     "genre": "Crime"},
    {"id": 550, "title": "Fight Club", "year": "1999", "director": "David Fincher",
     "description": "Un employé insomniaque et un vendeur de savon fondent un club de combat clandestin.",
     "image_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
     "genre": "Drama"},
    {"id": 278, "title": "The Shawshank Redemption", "year": "1994", "director": "Frank Darabont",
     "description": "Un banquier condamné à tort se lie d'amitié avec un détenu et trouve espoir en prison.",
     "image_url": "https://image.tmdb.org/t/p/w500/9cjIGRQL4apOeBUAVelXVB2V09a.jpg",
     "genre": "Drama"},
    {"id": 129, "title": "Spirited Away", "year": "2001", "director": "Hayao Miyazaki",
     "description": "Chihiro, 10 ans, entre dans un monde de esprits et doit sauver ses parents transformés en porcs.",
     "image_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
     "genre": "Animation"},
    {"id": 120467, "title": "The Grand Budapest Hotel", "year": "2014", "director": "Wes Anderson",
     "description": "Les aventures d'un concierge légendaire et de son protégé dans un hôtel européen.",
     "image_url": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg",
     "genre": "Comedy"},
    {"id": 872585, "title": "Oppenheimer", "year": "2023", "director": "Christopher Nolan",
     "description": "L'histoire de J. Robert Oppenheimer et la création de la bombe atomique.",
     "image_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
     "genre": "Drama"},
    {"id": 98, "title": "Gladiator", "year": "2000", "director": "Ridley Scott",
     "description": "Un général romain trahi devient gladiateur et cherche à venger sa famille assassinée.",
     "image_url": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
     "genre": "Action"},
    {"id": 6977, "title": "No Country for Old Men", "year": "2007", "director": "Joel & Ethan Coen",
     "description": "Un chasseur trouve deux millions de dollars et se retrouve traqué par un tueur implacable.",
     "image_url": "https://image.tmdb.org/t/p/w500/bj1v6YKF8yHqA489GFiMqTJMQpB.jpg",
     "genre": "Thriller"},
]

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
    53: "Thriller", 10752: "War", 37: "Western",
}


# --- base de donnees SQLite ---

def get_conn():
    """retourne une connexion sqlite avec row factory (acces par nom de colonne)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """cree la table si elle existe pas encore"""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS films (
            id           INTEGER PRIMARY KEY,
            title        TEXT NOT NULL,
            year         TEXT,
            director     TEXT,
            description  TEXT,
            image_url    TEXT,
            genre        TEXT,
            backdrop_url TEXT,
            tagline      TEXT,
            runtime      INTEGER,
            vote_average REAL,
            vote_count   INTEGER,
            trailer_key  TEXT,
            cast_json    TEXT,
            genres_json  TEXT,
            has_detail   INTEGER DEFAULT 0,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def count_films():
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    conn.close()
    return n


def upsert_film(conn, film):
    """insert ou met a jour un film (on ecrase pas le director si on le connait deja)"""
    conn.execute("""
        INSERT INTO films (id, title, year, director, description, image_url, genre, updated_at)
        VALUES (:id, :title, :year, :director, :description, :image_url, :genre, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            title       = excluded.title,
            year        = excluded.year,
            description = excluded.description,
            image_url   = excluded.image_url,
            genre       = excluded.genre,
            director    = CASE
                WHEN excluded.director != 'N/A' THEN excluded.director
                ELSE films.director
            END,
            updated_at  = CURRENT_TIMESTAMP
    """, film)


def upsert_detail(conn, detail):
    """met a jour les champs detail d'un film (trailer, cast, etc.)"""
    conn.execute("""
        UPDATE films SET
            director     = :director,
            backdrop_url = :backdrop_url,
            tagline      = :tagline,
            runtime      = :runtime,
            vote_average = :vote_average,
            vote_count   = :vote_count,
            trailer_key  = :trailer_key,
            cast_json    = :cast_json,
            genres_json  = :genres_json,
            has_detail   = 1,
            updated_at   = CURRENT_TIMESTAMP
        WHERE id = :id
    """, detail)


def get_films(limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM films ORDER BY updated_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_film_by_id(film_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM films WHERE id = ?", (film_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def search_in_db(query, limit=20):
    """recherche dans la db par titre, realisateur, genre, description"""
    q = f"%{query}%"
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM films
        WHERE lower(title)       LIKE lower(?)
           OR lower(director)    LIKE lower(?)
           OR lower(genre)       LIKE lower(?)
           OR lower(description) LIKE lower(?)
        LIMIT ?
    """, (q, q, q, q, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- appels TMDB ---

async def tmdb_get(endpoint, params=None):
    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{TMDB_BASE}{endpoint}",
            headers=headers,
            params=params or {},
        )
        res.raise_for_status()
        return res.json()


def normalize_tmdb_movie(m):
    """convertit un film tmdb au format de notre db"""
    genre_ids = m.get("genre_ids", [])
    genre = GENRE_MAP.get(genre_ids[0], "Unknown") if genre_ids else "Unknown"
    release = m.get("release_date", "") or ""
    poster = m.get("poster_path") or ""
    return {
        "id": m.get("id"),
        "title": m.get("title", "Unknown"),
        "year": release[:4] if len(release) >= 4 else "N/A",
        "director": "N/A",  # pas dispo dans /popular, recupere au detail
        "description": m.get("overview", ""),
        "image_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
        "genre": genre,
    }


# --- tache de rafraichissement ---

async def refresh_from_source():
    """recupere les films depuis TMDB (ou mock) et met a jour la db"""
    print("[refresh] debut du rafraichissement de la db...")
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/movie/popular", {"language": "fr-FR", "page": 1})
            films = [normalize_tmdb_movie(m) for m in data.get("results", [])][:20]
            conn = get_conn()
            for f in films:
                upsert_film(conn, f)
            conn.commit()
            conn.close()
            print(f"[refresh] {len(films)} films mis a jour depuis TMDB")
            return
        except Exception as e:
            print(f"[refresh] erreur TMDB: {e}, fallback sur mock")

    # pas de cle ou erreur → on charge les mocks
    conn = get_conn()
    for f in MOCK_MOVIES:
        upsert_film(conn, f)
    conn.commit()
    conn.close()
    print(f"[refresh] {len(MOCK_MOVIES)} films mock charges en db")


async def refresh_loop():
    """tourne en arriere-plan, rafraichit la db toutes les REFRESH_INTERVAL secondes"""
    while True:
        await asyncio.sleep(REFRESH_INTERVAL)
        try:
            await refresh_from_source()
        except Exception as e:
            print(f"[refresh] echec du cycle de rafraichissement: {e}")


# --- demarrage de l'app ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # au demarrage : init db puis chargement initial si vide
    init_db()
    if count_films() == 0:
        print("[startup] db vide, chargement initial...")
        await refresh_from_source()
    else:
        print(f"[startup] db deja chargee ({count_films()} films)")

    # lance la boucle de rafraichissement en arriere-plan
    task = asyncio.create_task(refresh_loop())
    yield
    # a l'arret on annule la tache
    task.cancel()


app = FastAPI(title="Films API", lifespan=lifespan)

# on autorise tout pour le CORS sinon le front peut pas fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- routes ---

@app.get("/hello")
async def hello():
    """health check + infos sur l'etat de la db"""
    mode = "tmdb" if TMDB_API_KEY else "mock"
    return {"status": "ok", "mode": mode, "films_en_db": count_films()}


@app.get("/movies")
async def get_movies(limit: int = Query(default=20, ge=1, le=100)):
    """retourne les films depuis la db (pas d'appel TMDB direct)"""
    return get_films(limit)


@app.get("/movie/{movie_id}")
async def get_movie_detail(movie_id: int = Path(...)):
    """detail d'un film - si pas en cache on fetch TMDB et on stocke en db"""
    film = get_film_by_id(movie_id)

    # si on a deja le detail complet en db, on retourne direct
    if film and film.get("has_detail"):
        film["cast"] = json.loads(film["cast_json"] or "[]")
        film["genres"] = json.loads(film["genres_json"] or "[]")
        return film

    # sinon on fetch le detail depuis TMDB et on le met en cache
    if TMDB_API_KEY and film:
        try:
            data = await tmdb_get(
                f"/movie/{movie_id}",
                {"language": "fr-FR", "append_to_response": "videos,credits"},
            )

            # chercher le realisateur dans le crew
            director = "N/A"
            for person in data.get("credits", {}).get("crew", []):
                if person.get("job") == "Director":
                    director = person["name"]
                    break

            # trailer youtube (fr de preference)
            trailer_key = None
            for v in data.get("videos", {}).get("results", []):
                if v.get("type") == "Trailer" and v.get("site") == "YouTube":
                    trailer_key = v["key"]
                    if v.get("iso_639_1") == "fr":
                        break

            # top 8 du casting
            cast_list = []
            for c in data.get("credits", {}).get("cast", [])[:8]:
                photo = None
                if c.get("profile_path"):
                    photo = f"https://image.tmdb.org/t/p/w185{c['profile_path']}"
                cast_list.append({
                    "name": c["name"],
                    "character": c["character"],
                    "photo": photo,
                })

            genres = [g["name"] for g in data.get("genres", [])]
            backdrop = data.get("backdrop_path") or ""
            poster = data.get("poster_path") or ""

            detail = {
                "id": movie_id,
                "director": director,
                "backdrop_url": f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else "",
                "tagline": data.get("tagline", ""),
                "runtime": data.get("runtime"),
                "vote_average": data.get("vote_average"),
                "vote_count": data.get("vote_count"),
                "trailer_key": trailer_key,
                "cast_json": json.dumps(cast_list),
                "genres_json": json.dumps(genres),
            }

            # on stocke le detail en db pour pas rappeler TMDB la prochaine fois
            conn = get_conn()
            upsert_detail(conn, detail)
            conn.commit()
            conn.close()

            film = get_film_by_id(movie_id)
            film["cast"] = cast_list
            film["genres"] = genres
            return film

        except Exception:
            pass  # fallback sur ce qu'on a en db

    # pas de cle ou erreur : on retourne ce qu'on a en db
    if film:
        film["cast"] = json.loads(film.get("cast_json") or "[]")
        film["genres"] = json.loads(film.get("genres_json") or "[]")
        film.setdefault("backdrop_url", "")
        film.setdefault("tagline", "")
        film.setdefault("trailer_key", None)
        return film

    return {"error": "Film non trouvé"}


@app.get("/search")
async def search_movies(q: str = Query(default="", min_length=0)):
    query = q.strip()
    if not query:
        return get_films(20)

    # si on a la cle on cherche sur tmdb et on stocke les resultats en db
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/search/movie", {"language": "fr-FR", "query": query})
            results = [normalize_tmdb_movie(m) for m in data.get("results", [])[:20]]
            conn = get_conn()
            for f in results:
                upsert_film(conn, f)
            conn.commit()
            conn.close()
            return results
        except Exception:
            pass

    # fallback : recherche dans la db locale
    return search_in_db(query)


# --- fichiers statiques (mode mono-conteneur) ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(static_dir, "index.html"))
