(() => {
  "use strict";

  // url du backend, peut etre override par config.js dans docker
  const API_BASE = window.__API_BASE || "http://localhost:8000";
  let currentLimit = 20;
  let currentPage = 1;
  let totalPages = 1;
  let searchTimer = null;
  let onlyFavs = false;   // filtre "mes favoris" actif ou pas

  // refs DOM
  const grid = document.getElementById("movies-grid");
  const counter = document.getElementById("movie-count");
  const modeEl = document.getElementById("mode-indicator");
  const resultsInfo = document.getElementById("results-info");
  const limitBtns = document.querySelectorAll(".limit-btn");
  const navbar = document.querySelector(".navbar");
  const searchInput = document.getElementById("search-input");
  const searchClear = document.getElementById("search-clear");
  const modal = document.getElementById("movie-modal");
  const modalContent = document.getElementById("modal-content");
  const pagination = document.getElementById("pagination");
  const favToggle = document.getElementById("fav-toggle");
  const favCount = document.getElementById("fav-count");

  // --- Favoris (localStorage) ---
  // On stocke un tableau d'IDs dans localStorage. Pas besoin de backend
  // pour ca : ca reste local au navigateur, c'est ce qu'on veut.
  const FAV_KEY = "cinescope_favs";

  function loadFavs() {
    try {
      const raw = localStorage.getItem(FAV_KEY);
      return new Set(raw ? JSON.parse(raw) : []);
    } catch (e) {
      return new Set();
    }
  }

  function saveFavs(set) {
    localStorage.setItem(FAV_KEY, JSON.stringify([...set]));
  }

  let favs = loadFavs();

  function isFav(id) { return favs.has(id); }

  function toggleFav(id) {
    if (favs.has(id)) favs.delete(id);
    else favs.add(id);
    saveFavs(favs);
    refreshFavCount();
  }

  function refreshFavCount() {
    favCount.textContent = favs.size;
  }
  refreshFavCount();

  // effet blur navbar au scroll
  let ticking = false;
  window.addEventListener("scroll", () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        navbar.classList.toggle("scrolled", window.scrollY > 10);
        ticking = false;
      });
      ticking = true;
    }
  });

  // observer pour l'animation d'entree des cartes
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.05 }
  );

  // affiche les placeholders de chargement
  function showSkeletons(nb) {
    grid.innerHTML = "";
    for (let i = 0; i < nb; i++) {
      const el = document.createElement("div");
      el.className = "skeleton-card";
      el.innerHTML = `
        <div class="skeleton-poster"></div>
        <div class="skeleton-body">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>`;
      grid.appendChild(el);
    }
  }

  function createCard(movie, index) {
    const card = document.createElement("article");
    card.className = "movie-card";
    card.style.animationDelay = `${index * 0.05}s`;

    const hasImg = movie.image_url && movie.image_url.length > 10;
    const fav = isFav(movie.id);

    card.innerHTML = `
      <div class="card-poster">
        ${hasImg
          ? `<img src="${movie.image_url}" alt="${movie.title}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
             <div class="card-poster-fallback" style="display:none">🎬</div>`
          : `<div class="card-poster-fallback">🎬</div>`
        }
        <span class="card-badge">${movie.genre}</span>
        <button class="fav-btn ${fav ? "active" : ""}" data-id="${movie.id}" title="${fav ? "Retirer des favoris" : "Ajouter aux favoris"}">${fav ? "♥" : "♡"}</button>
      </div>
      <div class="card-body">
        <div class="card-title">${movie.title}</div>
        <div class="card-meta">${movie.year}${movie.director && movie.director !== "N/A" ? ` · ${movie.director}` : ""}</div>
        <p class="card-desc">${movie.description}</p>
      </div>`;

    // bouton coeur : on stop la propag pour pas ouvrir la modal
    const favBtn = card.querySelector(".fav-btn");
    favBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleFav(movie.id);
      const nowFav = isFav(movie.id);
      favBtn.classList.toggle("active", nowFav);
      favBtn.textContent = nowFav ? "♥" : "♡";
      favBtn.title = nowFav ? "Retirer des favoris" : "Ajouter aux favoris";
      // si on est en mode "mes favoris" et qu'on retire, on re-render
      if (onlyFavs && !nowFav) fetchMovies();
    });

    // clic sur la carte -> ouvre le modal avec les details
    if (movie.id) {
      card.addEventListener("click", () => openModal(movie.id));
    }

    setTimeout(() => observer.observe(card), 10);
    return card;
  }

  // --- Modal detail film ---

  async function openModal(movieId) {
    modal.classList.add("active");
    document.body.style.overflow = "hidden";

    // spinner pendant le chargement
    modalContent.innerHTML = `<div class="modal-loading"><div class="modal-spinner"></div></div>`;

    try {
      const res = await fetch(`${API_BASE}/movie/${movieId}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // formatage note et duree
      const stars = data.vote_average ? `${data.vote_average.toFixed(1)}<span class="modal-vote-max">/10</span>` : "";
      let duree = "";
      if (data.runtime) {
        const h = Math.floor(data.runtime / 60);
        const min = String(data.runtime % 60).padStart(2, "0");
        duree = `${h}h${min}`;
      }

      const fav = isFav(movieId);

      modalContent.innerHTML = `
        <div class="modal-backdrop-wrap">
          ${data.backdrop_url ? `<img class="modal-backdrop" src="${data.backdrop_url}" alt="" />` : ""}
          <div class="modal-backdrop-fade"></div>
        </div>
        <button class="modal-close" aria-label="Fermer">&times;</button>
        <div class="modal-body">
          <div class="modal-poster-col">
            ${data.image_url ? `<img class="modal-poster" src="${data.image_url}" alt="${data.title}" />` : ""}
          </div>
          <div class="modal-info">
            ${data.tagline ? `<p class="modal-tagline">${data.tagline}</p>` : ""}
            <h2 class="modal-title">${data.title}</h2>
            <div class="modal-meta-row">
              ${data.year ? `<span>${data.year}</span>` : ""}
              ${duree ? `<span>${duree}</span>` : ""}
              ${stars ? `<span class="modal-rating">★ ${stars}</span>` : ""}
              ${data.vote_count ? `<span class="modal-votes">${data.vote_count.toLocaleString()} votes</span>` : ""}
              <button class="modal-fav-btn ${fav ? "active" : ""}" id="modal-fav-btn">${fav ? "♥ Favori" : "♡ Ajouter aux favoris"}</button>
            </div>
            <div class="modal-genres">
              ${(data.genres || []).map(g => `<span class="modal-genre-tag">${g}</span>`).join("")}
            </div>
            <p class="modal-overview">${data.description}</p>
            <div class="modal-director">
              <span class="modal-label">Réalisateur</span>
              <span>${data.director}</span>
            </div>
            ${data.cast && data.cast.length ? `
              <div class="modal-cast-section">
                <span class="modal-label">Casting</span>
                <div class="modal-cast-grid">
                  ${data.cast.map(c => `
                    <div class="modal-cast-item">
                      ${c.photo
                        ? `<img class="modal-cast-photo" src="${c.photo}" alt="${c.name}" onerror="this.style.display='none'" />`
                        : `<div class="modal-cast-photo modal-cast-placeholder">👤</div>`
                      }
                      <div class="modal-cast-name">${c.name}</div>
                      <div class="modal-cast-char">${c.character}</div>
                    </div>
                  `).join("")}
                </div>
              </div>
            ` : ""}
            ${data.trailer_key ? `
              <div class="modal-trailer-section">
                <span class="modal-label">Bande-annonce</span>
                <div class="modal-trailer-wrap">
                  <iframe
                    src="https://www.youtube.com/embed/${data.trailer_key}?rel=0"
                    title="Trailer"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                  ></iframe>
                </div>
              </div>
            ` : ""}
            <div class="modal-similar-section" id="modal-similar-section" style="display:none">
              <span class="modal-label">Films similaires</span>
              <div class="modal-similar-grid" id="modal-similar-grid"></div>
            </div>
          </div>
        </div>`;

      modalContent.querySelector(".modal-close").addEventListener("click", closeModal);

      // bouton favori dans la modal
      const modalFavBtn = modalContent.querySelector("#modal-fav-btn");
      modalFavBtn.addEventListener("click", () => {
        toggleFav(movieId);
        const nowFav = isFav(movieId);
        modalFavBtn.classList.toggle("active", nowFav);
        modalFavBtn.textContent = nowFav ? "♥ Favori" : "♡ Ajouter aux favoris";
        // sync avec le coeur sur la carte derriere si elle existe
        const cardBtn = grid.querySelector(`.fav-btn[data-id="${movieId}"]`);
        if (cardBtn) {
          cardBtn.classList.toggle("active", nowFav);
          cardBtn.textContent = nowFav ? "♥" : "♡";
        }
      });

      // films similaires (chargement async, ne bloque pas l'ouverture de la modal)
      loadSimilar(movieId);

    } catch (err) {
      modalContent.innerHTML = `
        <button class="modal-close" aria-label="Fermer">&times;</button>
        <div class="modal-error">Impossible de charger les détails du film.</div>`;
      modalContent.querySelector(".modal-close").addEventListener("click", closeModal);
    }
  }

  async function loadSimilar(movieId) {
    try {
      const res = await fetch(`${API_BASE}/movie/${movieId}/similar`);
      if (!res.ok) return;
      const list = await res.json();
      if (!Array.isArray(list) || list.length === 0) return;

      const section = document.getElementById("modal-similar-section");
      const wrap = document.getElementById("modal-similar-grid");
      if (!section || !wrap) return;

      wrap.innerHTML = list.slice(0, 6).map(m => `
        <div class="modal-similar-item" data-id="${m.id}">
          ${m.image_url
            ? `<img src="${m.image_url}" alt="${m.title}" onerror="this.style.display='none'" />`
            : `<div class="modal-similar-fallback">🎬</div>`}
          <div class="modal-similar-title">${m.title}</div>
          <div class="modal-similar-year">${m.year || ""}</div>
        </div>
      `).join("");

      // clic sur un similar -> on rouvre la modal avec ce film
      wrap.querySelectorAll(".modal-similar-item").forEach(el => {
        el.addEventListener("click", () => {
          const newId = parseInt(el.dataset.id, 10);
          if (newId) openModal(newId);
        });
      });

      section.style.display = "block";
    } catch (e) {
      // silencieux : on a deja l'essentiel de la modal, c'est juste un bonus
    }
  }

  function closeModal() {
    modal.classList.remove("active");
    document.body.style.overflow = "";
    // faut arreter la video sinon elle continue en fond
    const iframe = modalContent.querySelector("iframe");
    if (iframe) iframe.src = "";
  }

  // fermer le modal en cliquant en dehors ou avec echap
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("active")) closeModal();
  });

  // --- Etats vide / erreur ---

  function showEmpty(query) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>Aucun résultat</h3>
        <p>Aucun film trouvé pour « ${query} »</p>
      </div>`;
  }

  function showEmptyFavs() {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">♡</div>
        <h3>Aucun favori</h3>
        <p>Cliquez sur le cœur d'un film pour l'ajouter ici.</p>
      </div>`;
  }

  function showError(msg) {
    grid.innerHTML = `
      <div class="error-state">
        <div class="error-icon">!</div>
        <h3>Connexion impossible</h3>
        <p>${msg}</p>
        <button class="error-retry" onclick="window.__fetchMovies()">Réessayer</button>
      </div>`;
  }

  // --- Pagination UI ---

  function renderPagination() {
    // pas de pagination si recherche, mode favoris, ou une seule page
    if (searchInput.value.trim() || onlyFavs || totalPages <= 1) {
      pagination.innerHTML = "";
      return;
    }
    const prev = currentPage > 1
      ? `<button class="pag-btn" data-page="${currentPage - 1}">← Précédent</button>`
      : `<button class="pag-btn" disabled>← Précédent</button>`;
    const next = currentPage < totalPages
      ? `<button class="pag-btn" data-page="${currentPage + 1}">Suivant →</button>`
      : `<button class="pag-btn" disabled>Suivant →</button>`;
    pagination.innerHTML = `
      ${prev}
      <span class="pag-info">page ${currentPage} / ${totalPages}</span>
      ${next}`;
    pagination.querySelectorAll("[data-page]").forEach(btn => {
      btn.addEventListener("click", () => {
        currentPage = parseInt(btn.dataset.page, 10);
        fetchMovies();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    });
  }

  // --- Fetch principal ---

  async function fetchMovies() {
    const query = searchInput.value.trim();
    showSkeletons(query ? 8 : currentLimit);
    resultsInfo.innerHTML = "";
    pagination.innerHTML = "";

    // cas mode favoris : on n'appelle pas le backend, on filtre les favs locaux
    if (onlyFavs && !query) {
      const ids = [...favs];
      if (ids.length === 0) {
        showEmptyFavs();
        counter.textContent = 0;
        return;
      }
      try {
        // on recupere les details de chaque favori (les films sont en BDD vu
        // qu'on les a forcement deja ouverts/charges au moins une fois)
        const movies = [];
        for (const id of ids) {
          try {
            const r = await fetch(`${API_BASE}/movie/${id}`);
            const m = await r.json();
            if (!m.error) movies.push(m);
          } catch (e) { /* skip */ }
        }
        grid.innerHTML = "";
        if (movies.length === 0) {
          showEmptyFavs();
        } else {
          movies.forEach((m, i) => grid.appendChild(createCard(m, i)));
        }
        counter.textContent = movies.length;
        resultsInfo.innerHTML = `<span>${movies.length}</span> favori${movies.length !== 1 ? "s" : ""}`;
      } catch (e) {
        showError("Erreur de chargement des favoris.");
      }
      return;
    }

    try {
      // on construit l'url selon si c'est une recherche ou pas
      let url;
      if (query) {
        url = `${API_BASE}/search?q=${encodeURIComponent(query)}`;
      } else {
        // mode pagine : on demande page+page_size
        url = `${API_BASE}/movies?page=${currentPage}&page_size=${currentLimit}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // selon le mode, le backend renvoie soit une liste (search), soit un objet pagine
      let movies;
      if (Array.isArray(data)) {
        movies = data;
        totalPages = 1;
      } else if (data.items) {
        movies = data.items;
        totalPages = data.total_pages || 1;
      } else {
        movies = data.fallback || [];
      }

      grid.innerHTML = "";

      if (movies.length === 0 && query) {
        showEmpty(query);
      } else {
        movies.forEach((m, i) => grid.appendChild(createCard(m, i)));
      }

      counter.textContent = movies.length;

      if (query) {
        resultsInfo.innerHTML = `<span>${movies.length}</span> résultat${movies.length !== 1 ? "s" : ""} pour « ${query} »`;
      }

      renderPagination();

      // check le mode (tmdb live ou mock)
      try {
        const helloRes = await fetch(`${API_BASE}/hello`);
        const info = await helloRes.json();
        modeEl.textContent = info.mode === "tmdb" ? "live" : "mock";
      } catch (e) {
        modeEl.textContent = "mock";
      }
    } catch (e) {
      showError("Le backend ne répond pas. Vérifiez que le serveur tourne sur le port 8000.");
    }
  }

  window.__fetchMovies = fetchMovies;

  // recherche avec debounce de 300ms
  searchInput.addEventListener("input", () => {
    const hasValue = searchInput.value.length > 0;
    searchClear.classList.toggle("visible", hasValue);
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      currentPage = 1;   // une nouvelle recherche -> retour page 1
      fetchMovies();
    }, 300);
  });

  // bouton clear de la recherche
  searchClear.addEventListener("click", () => {
    searchInput.value = "";
    searchClear.classList.remove("visible");
    resultsInfo.innerHTML = "";
    currentPage = 1;
    fetchMovies();
    searchInput.focus();
  });

  // boutons de limite (6, 12, 20)
  limitBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      limitBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentLimit = parseInt(btn.dataset.limit, 10);
      currentPage = 1;   // changer la taille -> retour page 1
      if (!searchInput.value.trim()) fetchMovies();
    });
  });

  // bouton "Mes favoris"
  favToggle.addEventListener("click", () => {
    onlyFavs = !onlyFavs;
    favToggle.classList.toggle("active", onlyFavs);
    currentPage = 1;
    fetchMovies();
  });

  // on charge les films au demarrage
  fetchMovies();
})();
