"""
genere les 3 schemas du rapport :
- architecture.png  (3 couches + tmdb)
- pipeline.png      (gitlab ci/cd)
- kubernetes.png    (deployements, services, ingress, hpa)
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

# couleurs - alignees sur le frontend (#7c5cfc accent violet)
NAVY = "#18181b"      # texte principal (era #1e3a5f)
BLUE = "#7c5cfc"      # remplace par le violet d'accent du frontend
GREEN = "#10b981"
ORANGE = "#f59e0b"
RED = "#ef4444"
GRAY = "#71717a"
PURPLE = "#6a4be8"    # variante hover de l'accent


def box(ax, x, y, w, h, label, color=BLUE, fs=11):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.5, edgecolor=NAVY, facecolor=color
    )
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            color="white", fontsize=fs, fontweight="bold")


def arrow(ax, x1, y1, x2, y2, label="", color=NAVY):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="->,head_width=6,head_length=8",
        linewidth=1.6, color=color
    )
    ax.add_patch(a)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.08, label,
                ha="center", va="center", fontsize=8.5,
                color=color, style="italic",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none"))


def diagram_architecture():
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(6, 5.6, "Architecture Cinescope (3 couches + sources)",
            ha="center", fontsize=15, fontweight="bold", color=NAVY)

    # 3 couches principales
    box(ax, 0.3, 2.5, 2.0, 1.2, "Client\n(Navigateur)", color=GRAY)
    box(ax, 2.9, 2.5, 2.4, 1.2, "Frontend\nnginx + JS\n:8080", color=BLUE)
    box(ax, 5.9, 2.5, 2.4, 1.2, "Backend\nFastAPI Python\n:8000", color=GREEN)
    box(ax, 8.9, 2.5, 2.6, 1.2, "PostgreSQL 16\n(table films)\n:5432", color=PURPLE)

    # source externe
    box(ax, 9.2, 4.3, 2.0, 0.9, "TMDB API\n(externe)", color=ORANGE, fs=10)

    # fleches
    arrow(ax, 2.3, 3.1, 2.9, 3.1, "HTTP")
    arrow(ax, 5.3, 3.1, 5.9, 3.1, "fetch JSON")
    arrow(ax, 8.3, 3.1, 8.9, 3.1, "psycopg2")
    arrow(ax, 8.0, 3.7, 9.4, 4.3, "httpx", color=ORANGE)
    arrow(ax, 9.4, 4.3, 7.7, 3.7, "rafraichit", color=ORANGE)

    ax.text(6.0, 1.8, "Si TMDB indispo -> 20 films de demonstration en fallback",
            ha="center", fontsize=9, style="italic", color=RED,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef2f2", edgecolor=RED))

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "architecture.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[ok] {out}")


def diagram_pipeline():
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(6, 4.5, "Pipeline CI/CD GitLab (3 stages)",
            ha="center", fontsize=15, fontweight="bold", color=NAVY)

    box(ax, 0.5, 2.2, 2.6, 1.4, "test\n\npytest 11 tests\n+ Postgres service\n-> JUnit", color=BLUE)
    box(ax, 4.2, 3.0, 2.6, 1.0, "build backend\n(Docker)", color=GREEN)
    box(ax, 4.2, 1.6, 2.6, 1.0, "build frontend\n(Docker)", color=GREEN)
    box(ax, 7.7, 2.2, 1.4, 1.4, "GitLab\nRegistry", color=NAVY)
    box(ax, 9.6, 2.2, 2.0, 1.4, "deploy\n(simule)\nbranch=main", color=ORANGE)

    arrow(ax, 3.1, 2.9, 4.2, 3.5)
    arrow(ax, 3.1, 2.9, 4.2, 2.1)
    arrow(ax, 6.8, 3.5, 7.7, 3.1, "push")
    arrow(ax, 6.8, 2.1, 7.7, 2.7, "push")
    arrow(ax, 9.1, 2.9, 9.6, 2.9)

    ax.text(8.4, 1.6, "tag SHA + latest", ha="center", fontsize=8,
            color=GRAY, style="italic")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "pipeline.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[ok] {out}")


def diagram_kubernetes():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6, 7.5, "Deploiement Kubernetes (Minikube)",
            ha="center", fontsize=15, fontweight="bold", color=NAVY)

    # encadre namespace
    ns = mpatches.FancyBboxPatch(
        (0.3, 0.3), 11.4, 6.7,
        boxstyle="round,pad=0.05,rounding_size=0.1",
        linewidth=2, edgecolor=NAVY, facecolor="#fafafa", linestyle="--"
    )
    ax.add_patch(ns)
    ax.text(0.6, 6.85, "Namespace: cinescope", fontsize=11,
            color=NAVY, fontweight="bold")

    # ingress en haut
    box(ax, 4.2, 5.7, 3.6, 0.9, "Ingress nginx\nhost: cinescope.local\n/api -> backend  |  / -> frontend",
        color=ORANGE, fs=9)

    # configmap + secret
    box(ax, 0.7, 5.7, 1.8, 0.7, "ConfigMap\n(DB_HOST, ENV)", color=GRAY, fs=8)
    box(ax, 9.5, 5.7, 1.8, 0.7, "Secret\n(DB_PASSWORD, TMDB)", color=RED, fs=8)

    # frontend
    box(ax, 0.7, 4.0, 1.4, 0.9, "Pod\nfrontend\n#1", color=GREEN, fs=8)
    box(ax, 2.3, 4.0, 1.4, 0.9, "Pod\nfrontend\n#2", color=GREEN, fs=8)
    ax.text(2.2, 4.95, "Deployment frontend (HPA 2-4)",
            ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    box(ax, 0.7, 2.8, 3.0, 0.7, "Service frontend (ClusterIP/NodePort)", color=BLUE, fs=8)

    # backend
    box(ax, 4.5, 4.0, 1.4, 0.9, "Pod\nbackend\n#1", color=GREEN, fs=8)
    box(ax, 6.1, 4.0, 1.4, 0.9, "Pod\nbackend\n#2", color=GREEN, fs=8)
    ax.text(6.0, 4.95, "Deployment backend (HPA 2-5)",
            ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    box(ax, 4.5, 2.8, 3.0, 0.7, "Service backend (ClusterIP)", color=BLUE, fs=8)

    # postgres
    box(ax, 8.5, 4.0, 2.4, 0.9, "Pod\npostgres", color=PURPLE, fs=9)
    ax.text(9.7, 4.95, "Deployment postgres (1 replica)",
            ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    box(ax, 8.5, 2.8, 2.4, 0.7, "Service postgres (ClusterIP)", color=BLUE, fs=8)
    box(ax, 8.5, 1.6, 2.4, 0.7, "PVC 1Gi (persistance)", color=GRAY, fs=8)

    # client
    box(ax, 0.7, 0.7, 2.0, 0.7, "Navigateur client", color=GRAY, fs=8)

    # fleches
    arrow(ax, 1.7, 1.4, 4.5, 5.7, "HTTP", color=NAVY)        # client -> ingress
    arrow(ax, 4.5, 6.1, 2.5, 4.9, color=NAVY)                # ingress -> front
    arrow(ax, 7.5, 6.1, 6.0, 4.9, color=NAVY)                # ingress -> back
    arrow(ax, 1.5, 5.7, 5.0, 4.9, color=GRAY)                # configmap -> back
    arrow(ax, 10.4, 5.7, 7.0, 4.9, color=RED)                # secret -> back
    arrow(ax, 7.5, 3.5, 8.5, 3.5, "SQL", color=PURPLE)       # back -> postgres
    arrow(ax, 9.7, 2.8, 9.7, 2.3, color=GRAY)                # postgres -> pvc

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "kubernetes.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[ok] {out}")


if __name__ == "__main__":
    diagram_architecture()
    diagram_pipeline()
    diagram_kubernetes()
    print("\nFini :", OUT_DIR)
