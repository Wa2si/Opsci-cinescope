import os
import httpx
from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Films API")

# on autorise tout pour le CORS sinon le front peut pas fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"

# Films en dur au cas ou y'a pas de clé TMDB
# les image_url c'est les vrais posters tmdb
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

# mapping des genre_ids tmdb vers des noms lisibles
GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
    53: "Thriller", 10752: "War", 37: "Western",
}


# fonction utilitaire pour appeler l'api tmdb
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


def normalize_tmdb_movie(movie_data):
    """transforme un film tmdb en notre format standard"""
    genre_ids = movie_data.get("genre_ids", [])
    # on prend juste le premier genre, flemme de gerer une liste
    genre = GENRE_MAP.get(genre_ids[0], "Unknown") if genre_ids else "Unknown"
    release = movie_data.get("release_date", "") or ""
    poster = movie_data.get("poster_path") or ""
    return {
        "id": movie_data.get("id"),
        "title": movie_data.get("title", "Unknown"),
        "year": release[:4] if len(release) >= 4 else "N/A",
        "director": "N/A",  # pas dispo dans /popular, faut un appel en plus
        "description": movie_data.get("overview", ""),
        "image_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
        "genre": genre,
    }


# --- Routes ---

@app.get("/hello")
async def hello():
    """health check basique"""
    mode = "tmdb" if TMDB_API_KEY else "mock"
    return {"status": "ok", "mode": mode}


@app.get("/movies")
async def get_movies(limit: int = Query(default=20, ge=1, le=100)):
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/movie/popular", {"language": "fr-FR", "page": 1})
            films = [normalize_tmdb_movie(m) for m in data.get("results", [])]
            return films[:limit]
        except httpx.HTTPStatusError as e:
            # si la clé est invalide on fallback sur le mock
            if e.response.status_code == 401:
                return {"error": "Clé TMDB invalide", "fallback": MOCK_MOVIES[:limit]}
            return {"error": f"Erreur TMDB ({e.response.status_code})", "fallback": MOCK_MOVIES[:limit]}
        except httpx.RequestError:
            return {"error": "TMDB injoignable", "fallback": MOCK_MOVIES[:limit]}
    return MOCK_MOVIES[:limit]


@app.get("/movie/{movie_id}")
async def get_movie_detail(movie_id: int = Path(...)):
    """recup les details d'un film (avec videos + credits)"""
    if TMDB_API_KEY:
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

            # chercher un trailer youtube (fr de preference)
            trailer_key = None
            videos = data.get("videos", {}).get("results", [])
            for v in videos:
                if v.get("type") == "Trailer" and v.get("site") == "YouTube":
                    trailer_key = v["key"]
                    if v.get("iso_639_1") == "fr":
                        break  # on garde le fr si on le trouve

            # top 8 du casting
            cast_list = []
            for c in data.get("credits", {}).get("cast", [])[:8]:
                photo_url = None
                if c.get("profile_path"):
                    photo_url = f"https://image.tmdb.org/t/p/w185{c['profile_path']}"
                cast_list.append({
                    "name": c["name"],
                    "character": c["character"],
                    "photo": photo_url
                })

            genres = [g["name"] for g in data.get("genres", [])]
            backdrop = data.get("backdrop_path") or ""
            poster = data.get("poster_path") or ""

            return {
                "id": data["id"],
                "title": data.get("title", "Unknown"),
                "year": (data.get("release_date") or "")[:4],
                "director": director,
                "description": data.get("overview", ""),
                "tagline": data.get("tagline", ""),
                "image_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
                "backdrop_url": f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else "",
                "genre": ", ".join(genres),
                "genres": genres,
                "runtime": data.get("runtime"),
                "vote_average": data.get("vote_average"),
                "vote_count": data.get("vote_count"),
                "trailer_key": trailer_key,
                "cast": cast_list,
            }
        except httpx.HTTPStatusError:
            pass  # on fallback sur le mock en dessous
        except httpx.RequestError:
            pass

    # fallback mock si pas de clé ou erreur
    for m in MOCK_MOVIES:
        if m["id"] == movie_id:
            return {**m, "tagline": "", "backdrop_url": "", "genres": [m["genre"]],
                    "runtime": None, "vote_average": None, "vote_count": None,
                    "trailer_key": None, "cast": []}
    return {"error": "Film non trouvé"}


@app.get("/search")
async def search_movies(q: str = Query(default="", min_length=0)):
    query = q.strip().lower()
    if not query:
        return MOCK_MOVIES
    # si on a la clé on cherche sur tmdb directement
    if TMDB_API_KEY:
        try:
            data = await tmdb_get("/search/movie", {"language": "fr-FR", "query": query})
            return [normalize_tmdb_movie(m) for m in data.get("results", [])[:20]]
        except (httpx.HTTPStatusError, httpx.RequestError):
            pass  # fallback sur recherche locale
    # recherche basique dans les mocks
    res = [m for m in MOCK_MOVIES
           if query in m["title"].lower()
           or query in m["director"].lower()
           or query in m["genre"].lower()
           or query in m["description"].lower()]
    return res


# --- Fichiers statiques (mode mono-conteneur) ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(static_dir, "index.html"))
