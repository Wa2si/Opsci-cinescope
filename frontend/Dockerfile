FROM nginx:alpine

# on vire la page par defaut de nginx
RUN rm -rf /usr/share/nginx/html/*

# copie des fichiers du front
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/

# le navigateur fait les appels API donc il faut localhost (pas le nom du conteneur)
RUN echo 'window.__API_BASE = "http://localhost:8000";' > /usr/share/nginx/html/config.js

# on injecte config.js dans le html avant script.js
RUN sed -i 's|<script src="script.js">|<script src="config.js"></script>\n  <script src="script.js">|' /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
