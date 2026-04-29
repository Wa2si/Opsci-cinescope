import os
import csv
import io
import json
import time
import asyncio
import httpx
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response


START_TIME = time.time()  # pour /status

# config TMDB (clé chargée depuis l'env, sinon mode mock)
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"

# config postgres
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "cinescope")
DB_USER = os.getenv("DB_USER", "cinescope")
DB_PASS = os.getenv("DB_PASSWORD", "cinescope")

# refresh toutes les heures (3600s)
REFRESH_INTERVAL = 3600


# Films "mock" utilisés si pas de clé TMDB.
# TODO: idéalement à sortir dans un mock_movies.json mais bon, ça fait le job
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

# IDs de genre TMDB -> nom (pris depuis /genre/movie/list)
GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
    53: "Thriller", 10752: "War", 37: "Western",
}


# ============================================================
# Accès BDD
# ============================================================

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )


def wait_for_db(tries=30, delay=2):
    # Quand on lance docker-compose, postgres met quelques secondes à
    # accepter les connexions. On retry au lieu de crasher direct.
    for i in range(tries):
        try:
            c = get_conn()
            c.close()
            return
        except Exception as e:
            print(f"[db] pas encore pret ({i+1}/{tries}): {e}")
            time.sleep(delay)
    raise RuntimeError("postgres injoignable apres plusieurs essais")


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
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
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM films")
    n = cur.fetchone()[0]
    conn.close()
    return n


def upsert_film(conn, film):
    # Subtilité ON CONFLICT : si TMDB renvoie 'N/A' pour le director
    # (ce qui arrive sur l'endpoint /popular qui ne retourne pas le crew),
    # on garde la valeur déjà en base si on l'avait récup via le détail.
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO films (id, title, year, director, description, image_url, genre, updated_at)
        VALUES (%(id)s, %(title)s, %(year)s, %(director)s, %(description)s, %(image_url)s, %(genre)s, CURRENT_TIMESTAMP)
        ON CONFLICT (id) DO UPDATE SET
            title       = EXCLUDED.title,
            year        = EXCLUDED.year,
            description = EXCLUDED.description,
            image_url   = EXCLUDED.image_url,
            genre       = EXCLUDED.genre,
            director    = CASE
                WHEN EXCLUDED.director <> 'N/A' THEN EXCLUDED.director
                ELSE films.director
            END,
            updated_at  = CURRENT_TIMESTAMP
    """, film)


def upsert_detail(conn, detail):
    cur = conn.cursor()
    cur.execute("""
        UPDATE films SET
            director     = %(director)s,
            backdrop_url = %(backdrop_url)s,
            tagline      = %(tagline)s,
            runtime      = %(runtime)s,
            vote_average = %(vote_average)s,
            vote_count   = %(vote_count)s,
            trailer_key  = %(trailer_key)s,
            cast_json    = %(cast_json)s,
            genres_json  = %(genres_json)s,
            has_detail   = 1,
            updated_at   = CURRENT_TIMESTAMP
        WHERE id = %(id)s
    """, detail)


def _dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def get_films(limit=20):
    conn = get_conn()
    cur = _dict_cursor(conn)
    cur.execute("SELECT * FROM films ORDER BY updated_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_film_by_id(film_id):
    conn = get_conn()
    cur = _dict_cursor(conn)
    cur.execute("SELECT * FROM films WHERE id = %s", (film_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def search_in_db(query, limit=20):
    # Échappe % et _ avant de les passer à LIKE, sinon "100%" matche tout.
    safe = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    q = f"%{safe}%"
    conn = get_conn()
    cur = _dict_cursor(conn)
    cur.execute("""
        SELECT * FROM films
        WHERE lower(title)       LIKE lower(%s)
           OR lower(director)    LIKE lower(%s)
           OR lower(genre)       LIKE lower(%s)
           OR lower(description) LIKE lower(%s)
        LIMIT %s
    """, (q, q, q, q, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# Appels TMDB
# ============================================================

async def tmdb_get(endpoint, params=None):
    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{TMDB_BASE}{endpoint}", headers=headers, params=params or {})
        res.raise_for_status()
        return res.json()


def normalize_tmdb_movie(m):
    # On reformate un film TMDB pour qu'il rentre dans notre table.
    # /popular ne renvoie pas le réalisateur -> "N/A" en attendant le détail.
    genre_ids = m.get("genre_ids", [])
    genre = GENRE_MAP.get(genre_ids[0], "Unknown") if genre_ids else "Unknown"
    release = m.get("release_date", "") or ""
    poster = m.get("poster_path") or ""
    return {
        "id": m.get("id"),
        "title": m.get("title", "Unknown"),
        "year": release[:4] if len(release) >= 4 else "N/A",
        "director": "N/A",
        "description": m.get("overview", ""),
        "image_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
        "genre": genre,
    }


async def refresh_from_source():
    print("[refresh] mise a jour de la db...")
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/movie/popular", {"language": "fr-FR", "page": 1})
            films = [normalize_tmdb_movie(m) for m in data.get("results", [])][:20]
            conn = get_conn()
            for f in films:
                upsert_film(conn, f)
            conn.commit()
            conn.close()
            print(f"[refresh] {len(films)} films via TMDB")
            return
        except Exception as e:
            # Si TMDB tombe, on ne veut pas casser le serveur -> on bascule sur les mocks.
            print(f"[refresh] TMDB ko ({e}), fallback mock")

    conn = get_conn()
    for f in MOCK_MOVIES:
        upsert_film(conn, f)
    conn.commit()
    conn.close()
    print(f"[refresh] {len(MOCK_MOVIES)} films mock charges")


async def refresh_loop():
    while True:
        await asyncio.sleep(REFRESH_INTERVAL)
        try:
            await refresh_from_source()
        except Exception as e:
            print(f"[refresh] cycle ko: {e}")


# ============================================================
# Lifecycle (startup / shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # postgres peut etre lent a demarrer (surtout dans Compose)
    wait_for_db()
    init_db()
    if count_films() == 0:
        print("[startup] db vide, premier chargement")
        await refresh_from_source()
    else:
        print(f"[startup] db ok ({count_films()} films)")

    task = asyncio.create_task(refresh_loop())
    yield
    task.cancel()


app = FastAPI(title="Cinescope API", lifespan=lifespan)

# CORS: en dev on ouvre tout. En prod il faudrait restreindre à l'origine du front.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

@app.get("/hello")
async def hello():
    mode = "tmdb" if TMDB_API_KEY else "mock"
    return {"status": "ok", "mode": mode, "films_en_db": count_films()}


@app.get("/movies")
async def get_movies(limit: int = Query(default=20, ge=1, le=100)):
    return get_films(limit)


@app.get("/movie/{movie_id}")
async def get_movie_detail(movie_id: int = Path(...)):
    film = get_film_by_id(movie_id)

    # Si on a déjà le détail en cache, on renvoie direct (pas de re-call TMDB).
    if film and film.get("has_detail"):
        film["cast"] = json.loads(film["cast_json"] or "[]")
        film["genres"] = json.loads(film["genres_json"] or "[]")
        return film

    # Sinon on tape sur TMDB pour avoir le casting + le trailer.
    if TMDB_API_KEY and film:
        try:
            data = await tmdb_get(
                f"/movie/{movie_id}",
                {"language": "fr-FR", "append_to_response": "videos,credits"},
            )

            # Récupération du réalisateur (premier crew avec job=Director)
            director = "N/A"
            for person in data.get("credits", {}).get("crew", []):
                if person.get("job") == "Director":
                    director = person["name"]
                    break

            # Trailer YouTube : on prend la VF si dispo, sinon n'importe lequel
            trailer_key = None
            for v in data.get("videos", {}).get("results", []):
                if v.get("type") == "Trailer" and v.get("site") == "YouTube":
                    trailer_key = v["key"]
                    if v.get("iso_639_1") == "fr":
                        break

            # On garde les 8 premiers acteurs (suffisant pour la modal)
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

            conn = get_conn()
            upsert_detail(conn, detail)
            conn.commit()
            conn.close()

            film = get_film_by_id(movie_id)
            film["cast"] = cast_list
            film["genres"] = genres
            return film
        except Exception:
            # Si TMDB tombe pendant le détail, tant pis : on rend ce qu'on a en BDD.
            pass

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

    # On regarde d'abord en BDD. Si on trouve qqch on s'arrête là, pas la peine
    # de spammer TMDB. La BDD est notre cache.
    results = search_in_db(query)
    if results:
        return results

    # Rien en BDD -> on demande à TMDB et on upsert les résultats dans la table.
    # Comme ça la prochaine fois qu'on cherche pareil, ça sortira direct de la BDD.
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/search/movie", {"language": "fr-FR", "query": query})
            new_films = [normalize_tmdb_movie(m) for m in data.get("results", [])[:20]]
            if new_films:
                conn = get_conn()
                for f in new_films:
                    upsert_film(conn, f)
                conn.commit()
                conn.close()
            return new_films
        except Exception:
            pass

    return []


# --- exports (TME 3) ---

@app.get("/export/movies.json")
async def export_movies_json():
    films = get_films(limit=1000)
    return Response(
        content=json.dumps(films, ensure_ascii=False, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=movies_export.json"},
    )


@app.get("/export/movies.csv")
async def export_movies_csv():
    films = get_films(limit=1000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "title", "year", "director", "genre", "description"])
    for f in films:
        w.writerow([
            f.get("id", ""),
            f.get("title", ""),
            f.get("year", ""),
            f.get("director", ""),
            f.get("genre", ""),
            (f.get("description") or "").replace("\n", " "),
        ])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=movies_export.csv"},
    )


@app.get("/status")
async def status():
    # Petit dashboard pratique pour la démo de soutenance.
    up = int(time.time() - START_TIME)
    h = up // 3600
    m = (up % 3600) // 60
    s = up % 60
    return {
        "status": "running",
        "mode": "tmdb" if TMDB_API_KEY else "mock",
        "films_en_db": count_films(),
        "uptime": f"{h}h{m:02d}m{s:02d}s",
        "uptime_seconds": up,
        "refresh_interval_sec": REFRESH_INTERVAL,
    }


# Mode mono-conteneur (utilisé surtout pour le TME 5 §étape 3) :
# si un dossier static/ est présent, on sert aussi le front depuis le backend.
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(static_dir, "index.html"))
