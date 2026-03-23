(() => {
  "use strict";

  // url du backend, peut etre override par config.js dans docker
  const API_BASE = window.__API_BASE || "http://localhost:8000";
  let currentLimit = 20;
  let searchTimer = null;

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

    card.innerHTML = `
      <div class="card-poster">
        ${hasImg
          ? `<img src="${movie.image_url}" alt="${movie.title}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
             <div class="card-poster-fallback" style="display:none">🎬</div>`
          : `<div class="card-poster-fallback">🎬</div>`
        }
        <span class="card-badge">${movie.genre}</span>
      </div>
      <div class="card-body">
        <div class="card-title">${movie.title}</div>
        <div class="card-meta">${movie.year}${movie.director && movie.director !== "N/A" ? ` · ${movie.director}` : ""}</div>
        <p class="card-desc">${movie.description}</p>
      </div>`;

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
          </div>
        </div>`;

      modalContent.querySelector(".modal-close").addEventListener("click", closeModal);
    } catch (err) {
      modalContent.innerHTML = `
        <button class="modal-close" aria-label="Fermer">&times;</button>
        <div class="modal-error">Impossible de charger les détails du film.</div>`;
      modalContent.querySelector(".modal-close").addEventListener("click", closeModal);
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

  function showError(msg) {
    grid.innerHTML = `
      <div class="error-state">
        <div class="error-icon">!</div>
        <h3>Connexion impossible</h3>
        <p>${msg}</p>
        <button class="error-retry" onclick="window.__fetchMovies()">Réessayer</button>
      </div>`;
  }

  // --- Fetch principal ---

  async function fetchMovies() {
    const query = searchInput.value.trim();
    showSkeletons(query ? 8 : currentLimit);
    resultsInfo.innerHTML = "";

    try {
      // on construit l'url selon si c'est une recherche ou pas
      let url;
      if (query) {
        url = `${API_BASE}/search?q=${encodeURIComponent(query)}`;
      } else {
        url = `${API_BASE}/movies?limit=${currentLimit}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // parfois le backend renvoie {error, fallback} au lieu d'une liste
      const movies = Array.isArray(data) ? data : data.fallback || [];

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
    searchTimer = setTimeout(() => fetchMovies(), 300);
  });

  // bouton clear de la recherche
  searchClear.addEventListener("click", () => {
    searchInput.value = "";
    searchClear.classList.remove("visible");
    resultsInfo.innerHTML = "";
    fetchMovies();
    searchInput.focus();
  });

  // boutons de limite (6, 12, 20)
  limitBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      limitBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentLimit = parseInt(btn.dataset.limit, 10);
      if (!searchInput.value.trim()) fetchMovies();
    });
  });

  // on charge les films au demarrage
  fetchMovies();
})();
