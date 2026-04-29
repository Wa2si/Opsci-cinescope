"""
genere le rapport final du projet OPSCI Cinescope (PDF).
identite visuelle alignee sur le frontend : Inter + Poppins, accent violet,
fond sombre pour la couverture, cartes modernes pour le contenu.

usage : python3 docs/gen_rapport.py
sortie : docs/rapport_cinescope.pdf
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether, ListFlowable, ListItem,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.flowables import HRFlowable

DOCS_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(DOCS_DIR, "fonts")
IMG_DIR = os.path.join(DOCS_DIR, "img")
OUT_PDF = os.path.join(DOCS_DIR, "rapport_cinescope.pdf")


# --- enregistrement des polices (memes que le frontend) ---

def _reg(name, file):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS_DIR, file)))

_reg("Inter",          "Inter-Regular.ttf")
_reg("Inter-Bold",     "Inter-Bold.ttf")
_reg("Inter-Semi",     "Inter-SemiBold.ttf")
_reg("Poppins",        "Poppins-Bold.ttf")
_reg("Poppins-Extra",  "Poppins-ExtraBold.ttf")

from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Inter", normal="Inter", bold="Inter-Bold",
                   italic="Inter", boldItalic="Inter-Bold")


# --- palette identique au frontend ---

# fond sombre (couverture)
BG_DARK   = colors.HexColor("#09090b")
SURFACE   = colors.HexColor("#16161a")
SURFACE_2 = colors.HexColor("#1c1c21")

# accent violet
ACCENT      = colors.HexColor("#7c5cfc")
ACCENT_DARK = colors.HexColor("#6a4be8")
ACCENT_BG   = colors.HexColor("#f3efff")    # rgba(124,92,252,0.06) sur fond blanc
ACCENT_LINE = colors.HexColor("#d8cffd")

# texte (sur fond clair)
TEXT      = colors.HexColor("#18181b")
TEXT_2    = colors.HexColor("#52525b")
TEXT_MUTE = colors.HexColor("#a1a1aa")

# bordures et surfaces (clair)
BORDER    = colors.HexColor("#e4e4e7")
BG_SOFT   = colors.HexColor("#fafafa")
BG_CODE   = colors.HexColor("#0f0f12")     # bloc code en sombre, comme un terminal
TEXT_CODE = colors.HexColor("#e4e4e7")


# --- styles paragraphes ---

styles = getSampleStyleSheet()

H1 = ParagraphStyle(
    "H1", fontName="Poppins-Extra", fontSize=24, textColor=TEXT,
    spaceAfter=4, spaceBefore=12, alignment=TA_LEFT, leading=28,
)
H2 = ParagraphStyle(
    "H2", fontName="Poppins", fontSize=14, textColor=TEXT,
    spaceAfter=6, spaceBefore=14, leading=18,
)
H3 = ParagraphStyle(
    "H3", fontName="Inter-Semi", fontSize=11, textColor=TEXT,
    spaceAfter=4, spaceBefore=10, leading=14,
)
BODY = ParagraphStyle(
    "Body", fontName="Inter", fontSize=10, leading=16,
    spaceAfter=6, alignment=TA_JUSTIFY, textColor=TEXT_2,
)
LEAD = ParagraphStyle(  # paragraphe d'introduction (plus grand)
    "Lead", fontName="Inter", fontSize=11, leading=18,
    spaceAfter=10, alignment=TA_JUSTIFY, textColor=TEXT,
)
SECTION_LABEL = ParagraphStyle(  # le petit "01" violet au dessus des H1
    "SectionLabel", fontName="Inter-Semi", fontSize=8.5,
    textColor=ACCENT, spaceAfter=2, spaceBefore=4,
    leading=10,
)
CODE = ParagraphStyle(
    "Code", fontName="Courier", fontSize=8.5, leading=12,
    textColor=TEXT_CODE, backColor=BG_CODE,
    borderColor=BG_CODE, borderWidth=0,
    borderPadding=10, leftIndent=0, rightIndent=0,
    spaceAfter=10, spaceBefore=4,
)
BULLET = ParagraphStyle(
    "Bullet", fontName="Inter", fontSize=10, leading=15,
    leftIndent=14, bulletIndent=2, spaceAfter=3,
    textColor=TEXT_2,
)
CAPTION = ParagraphStyle(
    "Caption", fontName="Inter", fontSize=8.5, alignment=TA_CENTER,
    textColor=TEXT_MUTE, spaceAfter=14, leading=11,
)


# --- canvas: page de garde + entetes/pieds ---

def page_garde(canv, doc):
    """page de garde - thème sombre comme le frontend"""
    canv.saveState()
    width, height = A4

    # fond integralement sombre
    canv.setFillColor(BG_DARK)
    canv.rect(0, 0, width, height, fill=1, stroke=0)

    # gros point violet en haut (comme le .nav-dot)
    canv.setFillColor(ACCENT)
    canv.circle(width / 2 - 1.6*cm, height - 4.5*cm, 0.18*cm, fill=1, stroke=0)
    canv.setFillColor(colors.HexColor("#fafafa"))
    canv.setFont("Inter-Semi", 11)
    canv.drawString(width / 2 - 1.2*cm, height - 4.6*cm, "cinescope")

    # gros titre
    canv.setFillColor(colors.HexColor("#fafafa"))
    canv.setFont("Poppins-Extra", 64)
    canv.drawCentredString(width / 2, height - 8.5*cm, "Cinescope")

    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 12)
    canv.drawCentredString(width / 2, height - 9.6*cm,
                           "Catalogue de films full-stack")

    # ligne accent violette
    canv.setStrokeColor(ACCENT)
    canv.setLineWidth(2)
    canv.line(width / 2 - 1.5*cm, height - 10.3*cm,
              width / 2 + 1.5*cm, height - 10.3*cm)

    # bloc info en bas
    canv.setFillColor(SURFACE)
    canv.roundRect(2.5*cm, 4.5*cm, width - 5*cm, 9*cm, 12, fill=1, stroke=0)

    # label "Module"
    canv.setFillColor(ACCENT)
    canv.setFont("Inter-Semi", 8)
    canv.drawString(3.5*cm, 12.5*cm, "MODULE")
    canv.setFillColor(colors.HexColor("#fafafa"))
    canv.setFont("Inter", 11)
    canv.drawString(3.5*cm, 11.85*cm,
                    "OPSCI - Operations et services informatiques")

    canv.setFillColor(ACCENT)
    canv.setFont("Inter-Semi", 8)
    canv.drawString(3.5*cm, 10.7*cm, "AUTEUR (BINOME)")
    canv.setFillColor(colors.HexColor("#fafafa"))
    canv.setFont("Inter", 11)
    canv.drawString(3.5*cm, 10.05*cm, "Wassim Garbouj  -  L3 Informatique")
    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 9)
    canv.drawString(3.5*cm, 9.4*cm,
                    "(travail en binome conformement au sujet)")

    canv.setFillColor(ACCENT)
    canv.setFont("Inter-Semi", 8)
    canv.drawString(3.5*cm, 8.3*cm, "DATE")
    canv.setFillColor(colors.HexColor("#fafafa"))
    canv.setFont("Inter", 11)
    canv.drawString(3.5*cm, 7.65*cm, datetime.now().strftime("%d %B %Y"))

    canv.setFillColor(ACCENT)
    canv.setFont("Inter-Semi", 8)
    canv.drawString(3.5*cm, 6.55*cm, "TRAVAUX INTEGRES")
    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 9)
    items = [
        "TME 2 - Backend FastAPI + endpoints REST",
        "TME 3 - Donnees externes (TMDB) + export JSON / CSV",
        "TME 4 - Frontend HTML/CSS/JS + integration API",
        "TME 5 - Conteneurisation Docker (multi-services)",
        "TME 7 - Orchestration Kubernetes + autoscaling",
        "Projet final - PostgreSQL + Ingress + CI/CD GitLab",
    ]
    for i, t in enumerate(items):
        canv.drawString(3.5*cm, 5.95*cm - i*0.42*cm, "* " + t)

    # mention bas
    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 8)
    canv.drawCentredString(width / 2, 2.5*cm,
                           "Universite - 2025/2026")
    canv.drawCentredString(width / 2, 2.0*cm,
                           "Rapport de projet")

    canv.restoreState()


def page_normal(canv, doc):
    """en-tete + pied de page sur les pages courantes"""
    canv.saveState()
    width, height = A4

    # entete : petit point + brand a gauche, page a droite
    canv.setFillColor(ACCENT)
    canv.circle(2*cm + 0.08*cm, height - 1.05*cm, 0.08*cm, fill=1, stroke=0)
    canv.setFillColor(TEXT_2)
    canv.setFont("Inter-Semi", 8)
    canv.drawString(2.25*cm, height - 1.1*cm, "cinescope  /  rapport de projet")
    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 8)
    canv.drawRightString(width - 2*cm, height - 1.1*cm,
                         f"page {doc.page:02d}")

    # ligne fine
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(2*cm, height - 1.3*cm, width - 2*cm, height - 1.3*cm)

    # pied
    canv.line(2*cm, 1.3*cm, width - 2*cm, 1.3*cm)
    canv.setFillColor(TEXT_MUTE)
    canv.setFont("Inter", 8)
    canv.drawString(2*cm, 0.85*cm, "OPSCI 2025/2026")
    canv.drawRightString(width - 2*cm, 0.85*cm, "Wassim Garbouj")

    canv.restoreState()


# --- helpers contenu ---

def section_title(num, title):
    """rend un H1 precedee d'un petit numero violet"""
    return [
        Paragraph(num, SECTION_LABEL),
        Paragraph(title, H1),
        HRFlowable(width="20%", thickness=2, color=ACCENT,
                   spaceBefore=2, spaceAfter=14),
    ]


def img_or_placeholder(filename, w_cm=14, h_cm=8, caption=""):
    path = os.path.join(IMG_DIR, filename)
    flow = []
    if os.path.exists(path):
        img = Image(path, width=w_cm*cm, height=h_cm*cm, kind="proportional")
        img.hAlign = "CENTER"
        flow.append(img)
    else:
        t = Table([[f"image manquante : {filename}"]],
                  colWidths=[w_cm*cm], rowHeights=[h_cm*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), ACCENT_BG),
            ("BOX", (0, 0), (-1, -1), 1, ACCENT_LINE),
            ("TEXTCOLOR", (0, 0), (-1, -1), ACCENT),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, -1), "Inter"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        flow.append(t)
    if caption:
        flow.append(Spacer(1, 6))
        flow.append(Paragraph(f"{caption}", CAPTION))
    return flow


def code_block(text):
    """bloc de code en thème sombre (look 'terminal')"""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>")
    return Paragraph(
        f"<font face='Courier' color='#e4e4e7'>{safe}</font>",
        CODE,
    )


def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(t, BULLET), bulletColor=ACCENT, value="circle")
         for t in items],
        bulletType="bullet", start="circle", leftIndent=18,
    )


def card_table(rows, header=None, col_widths=None):
    """table 'card' avec lignes alternees et bordure subtile"""
    data = []
    if header:
        data.append(header)
    data.extend(rows)
    if not col_widths:
        col_widths = [4.5*cm, 11.5*cm]
    t = Table(data, colWidths=col_widths)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Inter"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_2),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1),
         [colors.white, BG_SOFT]),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT),
            ("FONTNAME", (0, 0), (-1, 0), "Inter-Semi"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
            ("TOPPADDING", (0, 0), (-1, 0), 9),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, ACCENT_LINE),
        ]
        # premiere colonne en accent semi-bold
        style += [
            ("FONTNAME", (0, 1), (0, -1), "Inter-Semi"),
            ("TEXTCOLOR", (0, 1), (0, -1), TEXT),
        ]
    else:
        style += [
            ("FONTNAME", (0, 0), (0, -1), "Inter-Semi"),
            ("TEXTCOLOR", (0, 0), (0, -1), TEXT),
        ]
    t.setStyle(TableStyle(style))
    return t


def info_box(text, kind="info"):
    """encart accent (avec barre violette a gauche)"""
    color = ACCENT if kind == "info" else colors.HexColor("#f59e0b")
    bg = ACCENT_BG if kind == "info" else colors.HexColor("#fef3c7")
    p = Paragraph(text, ParagraphStyle(
        "InfoText", fontName="Inter", fontSize=9.5, leading=14,
        textColor=TEXT, alignment=TA_LEFT,
    ))
    t = Table([[p]], colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


# --- contenu du rapport ---

def build_story():
    s = []
    s.append(PageBreak())   # commence apres la page de garde

    # ============ SOMMAIRE ============
    s.extend(section_title("00", "Sommaire"))

    toc_data = [
        ["01", "Introduction et contexte"],
        ["02", "Choix techniques et justifications"],
        ["03", "Architecture generale"],
        ["04", "Backend - FastAPI"],
        ["05", "Base de donnees - PostgreSQL"],
        ["06", "Frontend - HTML/CSS/JS"],
        ["07", "Conteneurisation - Docker"],
        ["08", "Orchestration - Kubernetes"],
        ["09", "CI/CD - GitLab"],
        ["10", "Tests"],
        ["11", "Difficultes rencontrees et solutions"],
        ["12", "Bilan et perspectives"],
        ["A",  "Annexes - commandes utiles"],
    ]
    toc_t = Table(toc_data, colWidths=[1.5*cm, 14.5*cm])
    toc_t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Inter-Semi"),
        ("TEXTCOLOR", (0, 0), (0, -1), ACCENT),
        ("FONTNAME", (1, 0), (1, -1), "Inter"),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    s.append(toc_t)
    s.append(PageBreak())

    # ============ 01. INTRODUCTION ============
    s.extend(section_title("01", "Introduction et contexte"))

    s.append(Paragraph(
        "Ce rapport presente <b>Cinescope</b>, une application web de catalogue "
        "de films developpee dans le cadre du module OPSCI. Le projet a ete "
        "construit progressivement au fil des seances de TME (TME 2 a TME 7) "
        "puis assemble en un projet final complet, conformement a l'esprit du "
        "sujet qui demande de rediger le rapport au fur et a mesure.", LEAD))

    s.append(Paragraph(
        "Le travail est realise <b>en binome</b> comme le demande explicitement "
        "le sujet, afin de se rapprocher d'un contexte reel de developpement. "
        "L'objectif n'est pas de produire l'application la plus complexe "
        "possible mais de demontrer notre capacite a concevoir, justifier, "
        "implementer et deployer une application complete dans une demarche "
        "proche des pratiques professionnelles.", BODY))

    s.append(Paragraph("Fonctionnalites principales", H3))
    s.append(bullet_list([
        "Catalogue de films avec affichage en grille",
        "Barre de recherche multi-champs (titre, realisateur, genre, description)",
        "Page de detail par film (cast, trailer YouTube, note, duree)",
        "Export des donnees en JSON et CSV",
        "Endpoint <b>/status</b> pour observer l'etat de l'application",
        "Mode mock automatique si la cle TMDB n'est pas fournie",
    ]))

    s.append(Spacer(1, 6))
    s.append(Paragraph("Perimetre technique couvert", H3))
    s.append(bullet_list([
        "Backend Python avec FastAPI (programmation asynchrone)",
        "Base de donnees PostgreSQL 16 (table films, requetes parametrees)",
        "Frontend HTML/CSS/JavaScript natif (pas de framework)",
        "Conteneurisation Docker des trois services (db, back, front)",
        "Orchestration Kubernetes (Pods, Services, Ingress, ConfigMap, Secret, HPA)",
        "Pipeline CI/CD GitLab (test, build, deploy) avec Postgres en service",
    ]))

    s.append(PageBreak())

    # ============ 02. CHOIX TECHNIQUES ============
    s.extend(section_title("02", "Choix techniques et justifications"))

    s.append(Paragraph(
        "Le sujet laisse les technologies au libre choix tant qu'elles sont "
        "<i>coherentes et justifiees</i>. Voici nos choix et les raisons qui "
        "nous ont amenes a les retenir.", BODY))

    s.append(Spacer(1, 6))
    s.append(card_table(
        rows=[
            ["Backend", "FastAPI (Python 3.11) - asynchrone natif, OpenAPI auto-genere, syntaxe simple a prendre en main pour des etudiants en L3"],
            ["Base de donnees", "PostgreSQL 16 - SQL standard largement utilise en entreprise, persistance via volume, types stricts"],
            ["Frontend", "HTML / CSS / JavaScript vanilla - pas de chaine de build, focus sur la comprehension du DOM et de fetch()"],
            ["Donnees", "API externe TMDB (option A du sujet) - donnees riches, mode mock pour developper sans cle"],
            ["Conteneurisation", "Docker + Docker Compose - 3 services orchestres simplement"],
            ["Orchestration", "Kubernetes via Minikube - pods, services, ingress, configmap, secret, HPA"],
            ["CI/CD", "GitLab CI (pipeline 3 stages : test, build, deploy)"],
            ["Tests", "pytest avec TestClient FastAPI"],
        ],
        header=["Composant", "Choix et justification"],
        col_widths=[3.5*cm, 12.5*cm],
    ))

    s.append(Paragraph("Pourquoi FastAPI plutot que Flask ou Django ?", H2))
    s.append(Paragraph(
        "FastAPI offre la programmation asynchrone (async/await) qui nous est "
        "utile pour les appels HTTP vers TMDB sans bloquer le serveur. Il "
        "genere aussi automatiquement une documentation Swagger interactive sur "
        "<b>/docs</b>, ce qui est tres pratique pour tester l'API pendant le "
        "developpement. Compare a Django, FastAPI est beaucoup plus leger et "
        "plus adapte a une API pure.", BODY))

    s.append(Paragraph("Pourquoi PostgreSQL plutot que MySQL ou MongoDB ?", H2))
    s.append(Paragraph(
        "Nos donnees (films) sont structurees et relationnelles, donc une base "
        "SQL est plus pertinente qu'une base NoSQL. Entre PostgreSQL et MySQL, "
        "nous avons choisi PostgreSQL car il est plus rigoureux sur les types "
        "et il supporte la clause <b>ON CONFLICT DO UPDATE</b> qui nous sert a "
        "faire un upsert propre lors du rafraichissement des donnees TMDB. "
        "C'est aussi la base la plus couramment utilisee en entreprise "
        "aujourd'hui.", BODY))

    s.append(Paragraph("Pourquoi pas de framework frontend ?", H2))
    s.append(Paragraph(
        "Nous avons commence le projet en HTML/CSS/JS natif au TME 4 et avons "
        "decide de ne pas ajouter de framework par la suite. Le perimetre est "
        "petit (un catalogue + une recherche + un modal), un framework comme "
        "React ou Vue aurait alourdi la chaine de build sans benefice reel. "
        "Cela nous a aussi force a comprendre <b>fetch()</b>, le DOM et "
        "<b>IntersectionObserver</b> a la main, ce qui est formateur.", BODY))

    s.append(Paragraph("Pourquoi Kubernetes alors que Compose suffit ?", H2))
    s.append(Paragraph(
        "Pour une application qui tourne en local, Docker Compose est largement "
        "suffisant. Nous avons quand meme deploye sur Kubernetes parce que "
        "c'etait demande par le sujet (TME 7 et section 8 du sujet final) et "
        "parce que cela nous a permis de manipuler des concepts pros : "
        "autoscaling (HPA), separation ConfigMap / Secret, Ingress avec "
        "routage, probes de sante.", BODY))

    s.append(PageBreak())

    # ============ 03. ARCHITECTURE ============
    s.extend(section_title("03", "Architecture generale"))

    s.append(Paragraph(
        "L'application suit une architecture <b>3 couches</b> classique : un "
        "client navigateur, un frontend statique servi par nginx, un backend "
        "API FastAPI et une base de donnees PostgreSQL. TMDB est une source "
        "de donnees externe que le backend interroge en arriere-plan.", LEAD))

    s.extend(img_or_placeholder("architecture.png", w_cm=15, h_cm=7,
        caption="Schema general - les fleches indiquent le sens des appels"))

    s.append(Paragraph("Flux de donnees", H2))
    s.append(bullet_list([
        "Au demarrage, le backend cree la table <b>films</b> dans Postgres si elle n'existe pas",
        "Si la table est vide, il appelle TMDB pour recuperer 20 films populaires",
        "Si TMDB n'est pas disponible (pas de cle), il insere 20 films de demonstration",
        "Toutes les heures, une tache de fond rafraichit les films depuis TMDB",
        "Le frontend appelle <b>/movies</b>, <b>/search</b>, <b>/movie/{id}</b> via fetch()",
        "Les details d'un film (cast, trailer) sont mis en cache en BDD apres le premier appel",
    ]))

    s.append(Spacer(1, 4))
    s.append(Paragraph("Schema de communication", H2))
    s.append(code_block(
        "Navigateur  --HTTP-->  Frontend (nginx)\n"
        "Frontend    --HTTP-->  Backend (FastAPI)\n"
        "Backend     --SQL -->  PostgreSQL\n"
        "Backend     --httpx->  TMDB API (rafraichissement uniquement)"
    ))

    s.append(PageBreak())

    # ============ 04. BACKEND ============
    s.extend(section_title("04", "Backend - FastAPI"))

    s.append(Paragraph(
        "Le backend tient dans un seul fichier <i>main.py</i>. Cette structure "
        "simple etait suffisante pour notre perimetre. Sur un projet plus gros "
        "nous aurions decoupe en plusieurs modules (routes, schemas, services).", BODY))

    s.append(Paragraph("Endpoints exposes", H2))
    s.append(card_table(
        rows=[
            ["GET /hello", "Healthcheck - retourne le mode (tmdb/mock) et le nombre de films en BDD"],
            ["GET /status", "Etat detaille - uptime, mode, nb films, intervalle de refresh"],
            ["GET /movies?limit=N", "Liste paginable des films (1 <= N <= 100)"],
            ["GET /movie/{id}", "Detail complet (realisateur, casting, trailer, synopsis)"],
            ["GET /search?q=...", "Recherche - tape sur TMDB si cle, sinon LIKE en BDD"],
            ["GET /export/movies.json", "Export JSON telechargeable"],
            ["GET /export/movies.csv", "Export CSV telechargeable"],
        ],
        header=["Route", "Role"],
        col_widths=[5*cm, 11*cm],
    ))

    s.append(Paragraph("Programmation asynchrone", H2))
    s.append(Paragraph(
        "Toutes les routes sont declarees <b>async</b> et les appels HTTP vers "
        "TMDB utilisent <b>httpx.AsyncClient</b>. Cela permet au serveur de "
        "traiter d'autres requetes pendant que TMDB repond. C'etait l'un des "
        "interets pedagogiques principaux de FastAPI.", BODY))

    s.append(code_block(
        "@app.get(\"/movies\")\n"
        "async def get_movies(limit: int = Query(default=20, ge=1, le=100)):\n"
        "    return get_films(limit)\n"
        "\n"
        "async def tmdb_get(endpoint, params=None):\n"
        "    async with httpx.AsyncClient(timeout=10) as client:\n"
        "        res = await client.get(f\"{TMDB_BASE}{endpoint}\", ...)\n"
        "        return res.json()"
    ))

    s.append(Paragraph("Tache de rafraichissement en arriere-plan", H2))
    s.append(Paragraph(
        "Au demarrage de l'application (lifespan), on lance une tache asyncio "
        "qui appelle <i>refresh_from_source()</i> toutes les heures. Si TMDB "
        "echoue on bascule sur les films mock pour que l'application continue "
        "de fonctionner.", BODY))

    s.append(code_block(
        "@asynccontextmanager\n"
        "async def lifespan(app):\n"
        "    wait_for_db()\n"
        "    init_db()\n"
        "    if count_films() == 0:\n"
        "        await refresh_from_source()\n"
        "    task = asyncio.create_task(refresh_loop())\n"
        "    yield\n"
        "    task.cancel()"
    ))

    s.append(PageBreak())

    # ============ 05. POSTGRES ============
    s.extend(section_title("05", "Base de donnees - PostgreSQL"))

    s.append(Paragraph(
        "La base contient une seule table <b>films</b> avec les colonnes "
        "essentielles pour l'affichage et la recherche, plus des champs "
        "optionnels pour le detail (cast, trailer, etc.) qui sont peuples "
        "lors du premier acces a la fiche d'un film.", BODY))

    s.append(Paragraph("Schema de la table", H2))
    s.append(code_block(
        "CREATE TABLE IF NOT EXISTS films (\n"
        "    id           INTEGER PRIMARY KEY,\n"
        "    title        TEXT NOT NULL,\n"
        "    year         TEXT,\n"
        "    director     TEXT,\n"
        "    description  TEXT,\n"
        "    image_url    TEXT,\n"
        "    genre        TEXT,\n"
        "    backdrop_url TEXT,\n"
        "    tagline      TEXT,\n"
        "    runtime      INTEGER,\n"
        "    vote_average REAL,\n"
        "    vote_count   INTEGER,\n"
        "    trailer_key  TEXT,\n"
        "    cast_json    TEXT,    -- liste JSON serialisee\n"
        "    genres_json  TEXT,    -- idem\n"
        "    has_detail   INTEGER DEFAULT 0,\n"
        "    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
        ");"
    ))

    s.append(Paragraph("Upsert avec ON CONFLICT", H2))
    s.append(Paragraph(
        "Pour synchroniser TMDB avec notre BDD, on utilise un <b>upsert</b> "
        "(INSERT ... ON CONFLICT DO UPDATE) qui ecrit le film s'il n'existe pas "
        "et le met a jour sinon. Petite subtilite : si TMDB renvoie 'N/A' pour "
        "le realisateur (cas de l'endpoint /popular), on garde l'ancienne "
        "valeur si on l'a deja recuperee via le detail.", BODY))

    s.append(code_block(
        "INSERT INTO films (id, title, year, director, ...)\n"
        "VALUES (%(id)s, %(title)s, ...)\n"
        "ON CONFLICT (id) DO UPDATE SET\n"
        "    title       = EXCLUDED.title,\n"
        "    director    = CASE\n"
        "        WHEN EXCLUDED.director <> 'N/A' THEN EXCLUDED.director\n"
        "        ELSE films.director\n"
        "    END,\n"
        "    updated_at  = CURRENT_TIMESTAMP"
    ))

    s.append(Paragraph("Recherche multi-champs", H2))
    s.append(Paragraph(
        "Quand TMDB n'est pas joignable, la route <b>/search</b> effectue une "
        "recherche SQL avec <b>LIKE</b> sur 4 colonnes (titre, realisateur, "
        "genre, description). Les caracteres % et _ sont echappes pour eviter "
        "les wildcards involontaires.", BODY))

    s.append(PageBreak())

    # ============ 06. FRONTEND ============
    s.extend(section_title("06", "Frontend - HTML/CSS/JS"))

    s.append(Paragraph(
        "Le frontend est compose de trois fichiers : <i>index.html</i> (la "
        "structure), <i>style.css</i> (theme sombre, glassmorphism, "
        "responsive) et <i>script.js</i> (logique fetch, recherche debounced, "
        "modal de detail). Servi par nginx sur le port 80 du conteneur (8080 "
        "en local).", BODY))

    s.append(Paragraph("Fonctionnalites principales", H2))
    s.append(bullet_list([
        "Affichage en grille avec animation d'apparition (IntersectionObserver)",
        "Recherche avec debounce de 300ms pour eviter de spam le backend",
        "Modal cliquable affichant le detail (poster, casting, trailer YouTube embarque)",
        "Boutons pour changer la limite (6 / 12 / 20 films)",
        "Indicateur visuel du mode (live TMDB / mock)",
        "Etat 'aucun resultat' et 'erreur de connexion' avec bouton retry",
    ]))

    s.append(Paragraph("Cycle d'un appel API", H2))
    s.append(code_block(
        "async function fetchMovies() {\n"
        "  showSkeletons(currentLimit);    // placeholders pendant le chargement\n"
        "  try {\n"
        "    const res = await fetch(`${API_BASE}/movies?limit=${currentLimit}`);\n"
        "    const movies = await res.json();\n"
        "    movies.forEach((m, i) => grid.appendChild(createCard(m, i)));\n"
        "  } catch (e) {\n"
        "    showError(\"Le backend ne repond pas.\");\n"
        "  }\n"
        "}"
    ))

    s.append(Paragraph("Captures d'ecran", H2))
    s.extend(img_or_placeholder("screen_app_home.png", w_cm=14, h_cm=8,
        caption="Page d'accueil - grille de films"))
    s.extend(img_or_placeholder("screen_app_modal.png", w_cm=14, h_cm=8,
        caption="Modal de detail (cast + trailer YouTube)"))

    s.append(PageBreak())

    # ============ 07. DOCKER ============
    s.extend(section_title("07", "Conteneurisation - Docker"))

    s.append(Paragraph(
        "Les trois composants (PostgreSQL, backend, frontend) sont encapsules "
        "dans des conteneurs Docker et orchestres avec Docker Compose. Le "
        "lancement complet du projet se fait avec une seule commande : "
        "<b>./start.sh</b> (qui appelle <i>docker compose up --build</i>).", BODY))

    s.append(Paragraph("Dockerfile backend", H2))
    s.append(code_block(
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "EXPOSE 8000\n"
        "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"
    ))

    s.append(Paragraph("docker-compose.yml (extrait)", H2))
    s.append(code_block(
        "services:\n"
        "  db:\n"
        "    image: postgres:16-alpine\n"
        "    environment:\n"
        "      POSTGRES_DB: cinescope\n"
        "      POSTGRES_USER: cinescope\n"
        "      POSTGRES_PASSWORD: cinescope\n"
        "    healthcheck:\n"
        "      test: [\"CMD-SHELL\", \"pg_isready -U cinescope\"]\n"
        "  backend:\n"
        "    build: ./backend\n"
        "    depends_on:\n"
        "      db:\n"
        "        condition: service_healthy\n"
        "    environment:\n"
        "      - DB_HOST=db\n"
        "      - TMDB_API_KEY=${TMDB_API_KEY:-}\n"
        "  frontend:\n"
        "    build: ./frontend\n"
        "    ports:\n"
        "      - \"8080:80\""
    ))

    s.append(info_box(
        "Le <b>healthcheck</b> sur Postgres + <b>depends_on: condition: "
        "service_healthy</b> evite que le backend demarre avant que la BDD "
        "soit prete (probleme courant avec Compose)."
    ))

    s.append(PageBreak())

    # ============ 08. K8S ============
    s.extend(section_title("08", "Orchestration - Kubernetes"))

    s.append(Paragraph(
        "Le projet est deployable sur un cluster Kubernetes via Minikube. Le "
        "script <i>k8s/deploy.sh</i> automatise la creation du namespace, "
        "l'application des manifests et l'attente que les pods soient prets.", BODY))

    s.extend(img_or_placeholder("kubernetes.png", w_cm=15.5, h_cm=8,
        caption="Vue logique du deploiement K8s"))

    s.append(Paragraph("Ressources deployees", H2))
    s.append(card_table(
        rows=[
            ["Namespace", "Isolation logique dans cinescope"],
            ["Deployment postgres", "1 replica + PVC 1Gi pour la persistance"],
            ["Deployment backend", "2 replicas, image films-backend:latest"],
            ["Deployment frontend", "2 replicas, image films-frontend:latest"],
            ["Services ClusterIP", "Communication interne (back -> db, front -> back)"],
            ["Service frontend NodePort", "Acces externe en fallback (port 30080)"],
            ["Ingress nginx", "Point d'entree unique : /api -> backend, / -> frontend"],
            ["ConfigMap", "Variables non sensibles (DB_HOST, DB_PORT, ENV, ...)"],
            ["Secret", "Variables sensibles (DB_PASSWORD, TMDB_API_KEY)"],
            ["HPA backend", "Autoscale 2-5 replicas selon CPU (cible 70%)"],
            ["HPA frontend", "Autoscale 2-4 replicas selon CPU (cible 70%)"],
            ["Probes", "readiness + liveness sur /hello (back), pg_isready (db)"],
        ],
        header=["Ressource", "Role"],
        col_widths=[5*cm, 11*cm],
    ))

    s.append(Paragraph("Ingress - point d'entree unique", H2))
    s.append(Paragraph(
        "L'Ingress remplace le NodePort comme entree principale : un seul "
        "hostname (<i>cinescope.local</i>) sert a la fois le frontend et "
        "l'API. Les requetes vers <b>/api</b> sont redirigees vers le backend, "
        "le reste vers le frontend. Cela imite ce qu'on ferait en production "
        "avec un domaine reel et HTTPS.", BODY))

    s.append(code_block(
        "apiVersion: networking.k8s.io/v1\n"
        "kind: Ingress\n"
        "spec:\n"
        "  ingressClassName: nginx\n"
        "  rules:\n"
        "    - host: cinescope.local\n"
        "      http:\n"
        "        paths:\n"
        "          - path: /api(/|$)(.*)\n"
        "            backend: { service: { name: backend, port: { number: 8000 } } }\n"
        "          - path: /\n"
        "            backend: { service: { name: frontend, port: { number: 80 } } }"
    ))

    s.append(Paragraph("Separation ConfigMap / Secret", H2))
    s.append(Paragraph(
        "On a separe les variables non sensibles (ConfigMap : DB_HOST, "
        "DB_NAME, ENV) des variables sensibles (Secret : DB_PASSWORD, "
        "TMDB_API_KEY). C'est une bonne pratique : les Secrets peuvent etre "
        "audites et chiffres separement, et seuls les pods qui en ont besoin "
        "y ont acces via RBAC.", BODY))

    s.append(Paragraph("Autoscaling", H2))
    s.append(Paragraph(
        "Le HPA (HorizontalPodAutoscaler) ajuste automatiquement le nombre de "
        "replicas du backend (2 a 5) et du frontend (2 a 4) selon "
        "l'utilisation CPU moyenne. Necessite l'addon metrics-server, active "
        "automatiquement par notre script de deploiement.", BODY))

    s.extend(img_or_placeholder("screen_kubectl.png", w_cm=14.5, h_cm=6.5,
        caption="kubectl get all - apercu des ressources deployees"))

    s.append(PageBreak())

    # ============ 09. CI/CD ============
    s.extend(section_title("09", "CI/CD - GitLab"))

    s.append(Paragraph(
        "Le depot est heberge sur GitLab et un pipeline CI/CD se declenche a "
        "chaque push. Trois stages s'enchainent : test, build, deploy.", BODY))

    s.extend(img_or_placeholder("pipeline.png", w_cm=15, h_cm=6,
        caption="Pipeline GitLab CI - 3 stages (test -> build -> deploy)"))

    s.append(Paragraph("Stage test", H2))
    s.append(Paragraph(
        "Lance les 11 tests pytest du backend. Une <b>Postgres en service</b> "
        "est demarree par GitLab pour que les tests aient une vraie BDD a "
        "interroger. Le rapport JUnit est genere et expose dans l'interface "
        "GitLab (onglet Tests).", BODY))

    s.append(code_block(
        "test-backend:\n"
        "  stage: test\n"
        "  image: python:3.11-slim\n"
        "  services:\n"
        "    - name: postgres:16-alpine\n"
        "      alias: postgres\n"
        "  script:\n"
        "    - cd backend\n"
        "    - pip install -r requirements.txt\n"
        "    - pytest -v --junitxml=report.xml\n"
        "  artifacts:\n"
        "    reports: { junit: backend/report.xml }"
    ))

    s.append(Paragraph("Stage build", H2))
    s.append(Paragraph(
        "Build des images Docker du backend et du frontend en parallele "
        "(<i>needs: test-backend</i>) avec Docker-in-Docker. Les images sont "
        "poussees vers la <b>GitLab Container Registry</b> avec deux tags : le "
        "SHA court du commit et <i>latest</i>.", BODY))

    s.append(Paragraph("Stage deploy", H2))
    s.append(Paragraph(
        "Pour ce projet etudiant, le deploiement reel sur un cluster est "
        "simule (on affiche les images publiees). Sur un projet pro on "
        "ferait <i>kubectl apply</i> ou <i>helm upgrade</i>. Cette etape ne se "
        "declenche que sur la branche <i>main</i> via une regle.", BODY))

    s.extend(img_or_placeholder("screen_pipeline.png", w_cm=14.5, h_cm=6.5,
        caption="Vue d'un pipeline reussi dans GitLab"))

    s.append(PageBreak())

    # ============ 10. TESTS ============
    s.extend(section_title("10", "Tests"))

    s.append(Paragraph(
        "Le backend est couvert par <b>11 tests pytest</b> qui exercent les "
        "principales routes. Les tests utilisent <b>TestClient</b> de FastAPI "
        "comme un context manager pour declencher le lifespan (init BDD, "
        "chargement initial). En CI, une vraie Postgres est utilisee comme "
        "service.", BODY))

    s.append(Paragraph("Tests existants", H2))
    s.append(bullet_list([
        "<b>test_hello</b> : healthcheck",
        "<b>test_movies_returns_list</b> / <b>_default</b> / <b>_have_id</b> : route /movies",
        "<b>test_movie_detail</b> : detail d'Inception (id 27205)",
        "<b>test_movie_not_found</b> : id inconnu -> {error}",
        "<b>test_search</b> / <b>_no_results</b> : recherche par mot-cle",
        "<b>test_export_json</b> / <b>_csv</b> : exports avec headers Content-Disposition",
        "<b>test_status</b> : route /status (uptime, mode, films_en_db)",
    ]))

    s.append(Paragraph("Exemple", H2))
    s.append(code_block(
        "def test_hello(client):\n"
        "    resp = client.get(\"/hello\")\n"
        "    assert resp.status_code == 200\n"
        "    data = resp.json()\n"
        "    assert data[\"status\"] == \"ok\"\n"
        "    assert data[\"mode\"] in (\"tmdb\", \"mock\")\n"
        "    assert data[\"films_en_db\"] > 0"
    ))

    s.append(PageBreak())

    # ============ 11. DIFFICULTES ============
    s.extend(section_title("11", "Difficultes rencontrees et solutions"))

    s.append(Paragraph(
        "Cette section regroupe les problemes concrets que nous avons "
        "rencontres et la maniere dont nous les avons resolus. C'est la "
        "partie la plus instructive de ce projet.", LEAD))

    s.append(Paragraph("Le backend demarrait avant Postgres", H2))
    s.append(Paragraph(
        "Avec Docker Compose, le backend se lancait avant que Postgres ait "
        "fini d'initialiser sa BDD. Resultat : crash au demarrage avec "
        "<i>connection refused</i>.", BODY))
    s.append(info_box(
        "<b>Solution :</b> ajout d'un healthcheck Postgres dans le compose "
        "(<i>pg_isready</i>) et utilisation de <i>depends_on: condition: "
        "service_healthy</i>. En complement, le backend possede une boucle "
        "<i>wait_for_db()</i> qui retry 30 fois pour les cas ou Compose ne "
        "suffit pas (cas Kubernetes notamment)."
    ))
    s.append(Spacer(1, 6))

    s.append(Paragraph("Migration SQLite -> PostgreSQL", H2))
    s.append(Paragraph(
        "Au depart on avait commence avec SQLite parce que c'est plus simple "
        "(juste un fichier). Mais le sujet du projet demande explicitement "
        "PostgreSQL, MySQL, MongoDB, etc. Il a fallu migrer.", BODY))
    s.append(info_box(
        "<b>Solution :</b> remplacement de <i>sqlite3</i> par <i>psycopg2</i>. "
        "Le plus delicat etait les placeholders (<i>?</i> -> <i>%s</i>) et le "
        "fait que psycopg2 utilise un cursor explicite. Heureusement la clause "
        "<i>ON CONFLICT DO UPDATE</i> existe dans les deux moteurs, le code "
        "SQL n'a quasi pas change."
    ))
    s.append(Spacer(1, 6))

    s.append(Paragraph("Les tests echouaient en CI sans BDD", H2))
    s.append(Paragraph(
        "Une fois passe a Postgres, les tests pytest ne pouvaient plus "
        "tourner sans un serveur de BDD lance.", BODY))
    s.append(info_box(
        "<b>Solution :</b> ajouter un <i>service: postgres:16-alpine</i> dans "
        "le job test du <i>.gitlab-ci.yml</i>. GitLab demarre alors le "
        "conteneur Postgres en parallele du conteneur Python et expose "
        "l'alias <i>postgres</i> comme nom de hote."
    ))
    s.append(Spacer(1, 6))

    s.append(Paragraph("Erreur YAML dans le pipeline", H2))
    s.append(Paragraph(
        "Au debut, le job <i>build-backend</i> echouait avec une erreur de "
        "syntaxe YAML parce qu'on avait ecrit un <i>docker tag</i> sur "
        "plusieurs lignes avec des <i>&amp;&amp;</i>.", BODY))
    s.append(info_box(
        "<b>Solution :</b> remettre la commande <i>docker tag SOURCE DEST</i> "
        "sur une seule ligne, ce que YAML attendait."
    ))
    s.append(Spacer(1, 6))

    s.append(Paragraph("PageBreak() oublie dans le rapport PDF", H2))
    s.append(Paragraph(
        "Lors de la generation du PDF, le contenu du sommaire se "
        "superposait avec la page de garde. La fonction <i>onFirstPage</i> "
        "dessinait la page de garde mais le contenu du <i>story</i> commencait "
        "aussi sur la meme page.", BODY))
    s.append(info_box(
        "<b>Solution :</b> ajouter un <i>PageBreak()</i> en tout premier "
        "element du <i>story</i>, ce qui force le contenu a commencer page 2 "
        "tandis que <i>onFirstPage</i> peint sa page de garde page 1."
    ))
    s.append(Spacer(1, 6))

    s.append(Paragraph("Choix entre framework et vanilla JS", H2))
    s.append(Paragraph(
        "On a hesite a utiliser React pour le front. On a finalement garde "
        "vanilla JS parce que :", BODY))
    s.append(bullet_list([
        "L'application n'a pas besoin de gestion d'etat complexe",
        "On voulait eviter d'ajouter un build step (npm install, vite build)",
        "On preferait travailler directement sur fetch() / DOM pour mieux comprendre",
    ]))
    s.append(Paragraph(
        "Si on devait recommencer sur un projet plus gros, on partirait sur "
        "Vite + React.", BODY))

    s.append(Paragraph("Migration GitHub -> GitLab", H2))
    s.append(Paragraph(
        "Le projet a debute sur GitHub puis a ete migre sur GitLab. La "
        "pipeline <i>github actions</i> a ete reecrite en <i>.gitlab-ci.yml</i>, "
        "et le push initial necessitait un Personal Access Token avec scope "
        "<i>write_repository</i>.", BODY))

    s.append(PageBreak())

    # ============ 12. BILAN ============
    s.extend(section_title("12", "Bilan et perspectives"))

    s.append(Paragraph("Ce qui fonctionne bien", H2))
    s.append(bullet_list([
        "Lancement complet du projet en une seule commande (<i>./start.sh</i>)",
        "11 tests automatises qui passent en CI sur une vraie Postgres",
        "Deploiement K8s reproductible via <i>./k8s/deploy.sh</i>",
        "Mode mock automatique : l'application demarre meme sans cle TMDB",
        "Persistance des donnees (volume Compose / PVC K8s) - les films restent",
        "Cache des details TMDB en BDD : on n'appelle l'API qu'une seule fois par film",
    ]))

    s.append(Paragraph("Ce qu'on aurait fait avec plus de temps", H2))
    s.append(bullet_list([
        "Mode <i>favoris</i> persistes (table <i>users_favorites</i>)",
        "Recommandations \"films similaires\" (basees sur le genre / realisateur)",
        "Cache Redis pour les requetes <b>/movies</b> frequentes",
        "Frontend reecrit en React + Vite pour gagner en organisation",
        "Authentification (JWT) pour proteger /export et l'admin",
        "TLS sur l'Ingress avec cert-manager + Let's Encrypt en prod",
    ]))

    s.append(Paragraph("Ce que le projet nous a appris", H2))
    s.append(bullet_list([
        "Structurer une application en 3 couches et choisir des outils coherents",
        "Manipuler une vraie BDD relationnelle (schema, requetes parametrees, upsert)",
        "Lire et appliquer une documentation d'API externe (TMDB)",
        "Conteneuriser une application multi-services et gerer les dependances",
        "Comprendre les concepts cles de Kubernetes (Pods, Services, Ingress, HPA)",
        "Mettre en place une CI/CD complete avec services et registry",
        "Travailler en binome avec un depot git partage",
    ]))

    s.append(PageBreak())

    # ============ ANNEXES ============
    s.extend(section_title("A", "Annexes - commandes utiles"))

    s.append(Paragraph("Lancement local", H2))
    s.append(code_block(
        "# tout lancer\n"
        "./start.sh             # ou : docker compose up --build\n"
        "\n"
        "# en arriere-plan\n"
        "docker compose up -d\n"
        "\n"
        "# logs\n"
        "docker compose logs -f backend\n"
        "\n"
        "# tout arreter (et supprimer le volume postgres)\n"
        "docker compose down -v"
    ))

    s.append(Paragraph("Tests", H2))
    s.append(code_block(
        "# postgres doit tourner pour les tests\n"
        "docker compose up -d db\n"
        "cd backend\n"
        "pip install -r requirements.txt\n"
        "pytest test_main.py -v"
    ))

    s.append(Paragraph("Deploiement Kubernetes", H2))
    s.append(code_block(
        "cd k8s\n"
        "./deploy.sh            # installe tout, attend que les pods soient prets\n"
        "\n"
        "# observer\n"
        "kubectl -n cinescope get all\n"
        "kubectl -n cinescope get hpa\n"
        "kubectl -n cinescope get ingress\n"
        "kubectl -n cinescope logs -l tier=backend --tail=50\n"
        "\n"
        "# scaler manuellement\n"
        "kubectl -n cinescope scale deployment backend --replicas=4\n"
        "\n"
        "# acceder via Ingress\n"
        "echo \"$(minikube ip) cinescope.local\" | sudo tee -a /etc/hosts\n"
        "# puis ouvrir http://cinescope.local\n"
        "\n"
        "# nettoyer\n"
        "./teardown.sh"
    ))

    s.append(Paragraph("Quelques requetes utiles", H2))
    s.append(code_block(
        "curl http://localhost:8000/hello\n"
        "curl http://localhost:8000/status\n"
        "curl 'http://localhost:8000/movies?limit=5'\n"
        "curl 'http://localhost:8000/search?q=nolan'\n"
        "curl http://localhost:8000/export/movies.csv -o films.csv"
    ))

    s.append(Paragraph("Structure du depot", H2))
    s.append(code_block(
        ".\n"
        "+-- backend/                   API FastAPI\n"
        "|   +-- main.py\n"
        "|   +-- test_main.py\n"
        "|   +-- requirements.txt\n"
        "|   +-- Dockerfile\n"
        "+-- frontend/                  SPA legere (HTML/CSS/JS)\n"
        "+-- k8s/                       Manifests Kubernetes\n"
        "|   +-- namespace.yaml\n"
        "|   +-- configmap.yaml secret.yaml\n"
        "|   +-- postgres-{deployment,service,pvc}.yaml\n"
        "|   +-- backend-{deployment,service,hpa}.yaml\n"
        "|   +-- frontend-{deployment,service,hpa}.yaml\n"
        "|   +-- ingress.yaml\n"
        "|   +-- deploy.sh teardown.sh\n"
        "+-- docs/                      Generation du rapport PDF\n"
        "+-- docker-compose.yml\n"
        "+-- .gitlab-ci.yml\n"
        "+-- start.sh\n"
        "+-- README.md"
    ))

    s.append(Spacer(1, 18))
    s.append(HRFlowable(width="100%", thickness=0.4, color=BORDER,
                        spaceBefore=4, spaceAfter=8))
    s.append(Paragraph(
        "Rapport genere automatiquement avec reportlab + matplotlib.<br/>"
        "Polices : Inter et Poppins (memes que le frontend).",
        CAPTION))

    return s


def main():
    doc = SimpleDocTemplate(
        OUT_PDF, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Cinescope - Rapport de projet",
        author="Wassim Garbouj",
    )

    story = build_story()
    doc.build(story, onFirstPage=page_garde, onLaterPages=page_normal)
    size = os.path.getsize(OUT_PDF) / 1024
    print(f"[ok] {OUT_PDF} ({size:.1f} Ko)")


if __name__ == "__main__":
    main()
