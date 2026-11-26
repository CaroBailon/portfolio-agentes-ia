"""Configuración leída de variables de entorno (o de un archivo .env)."""

import os
from pathlib import Path

try:  # python-dotenv es opcional: si está instalado, lee el archivo .env
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

RAIZ = Path(__file__).resolve().parent.parent
REPO = RAIZ.parent

# La base de conocimiento y los casos de prueba son los mismos de la versión en Make:
# así las dos versiones se comparan sobre el mismo material.
RUTA_BASE = Path(os.environ.get(
    "ARI_BASE_CONOCIMIENTO", REPO / "03_ARI_FLOW_Agent" / "base_conocimiento_oracle_sales.txt"))
RUTA_CASOS = Path(os.environ.get(
    "ARI_CASOS", REPO / "03_ARI_FLOW_Agent" / "evaluacion" / "casos_de_prueba.csv"))
RUTA_CHROMA = Path(os.environ.get("ARI_CHROMA_DIR", RAIZ / ".chroma"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODELO_TEXTO = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
MODELO_EMBEDDINGS = os.environ.get("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# Cuántos fragmentos de la base se recuperan para cada correo.
TOP_K = int(os.environ.get("ARI_TOP_K", "4"))

# Si está definido, el webhook exige este valor en el encabezado X-Webhook-Token.
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
