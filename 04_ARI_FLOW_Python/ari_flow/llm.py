"""Acceso a los modelos. El agente depende de estas dos interfaces, no de Gemini.

Separarlo así permite cambiar de proveedor (OpenAI, Claude, un modelo local) tocando un
solo archivo, y probar el resto del agente con modelos simulados, sin gastar llamadas.
"""

import json
import time
from typing import Protocol

from . import config


class ModeloTexto(Protocol):
    def generar_json(self, sistema: str, mensaje: str, esquema: dict) -> dict: ...

    def generar_texto(self, sistema: str, mensaje: str) -> str: ...


class ModeloEmbeddings(Protocol):
    def embeber(self, textos: list[str], es_consulta: bool) -> list[list[float]]: ...


def _con_reintentos(funcion, intentos: int = 4):
    """Reintenta ante límites de uso (429) o errores temporales, esperando cada vez más."""
    for intento in range(intentos):
        try:
            return funcion()
        except Exception as error:  # el SDK usa varias clases de error según el caso
            texto = str(error)
            temporal = any(c in texto for c in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"))
            if not temporal or intento == intentos - 1:
                raise
            time.sleep(5 * 2 ** intento)


class Gemini:
    """Implementación con la API de Google Gemini (paquete google-genai)."""

    def __init__(self, api_key: str | None = None):
        from google import genai

        clave = api_key or config.GEMINI_API_KEY
        if not clave:
            raise RuntimeError("Falta GEMINI_API_KEY. Copiá .env.example a .env y completala.")
        self._cliente = genai.Client(api_key=clave)

    def generar_json(self, sistema: str, mensaje: str, esquema: dict) -> dict:
        from google.genai import types

        respuesta = _con_reintentos(lambda: self._cliente.models.generate_content(
            model=config.MODELO_TEXTO,
            contents=mensaje,
            config=types.GenerateContentConfig(
                system_instruction=sistema,
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=esquema,
            ),
        ))
        return json.loads(respuesta.text)

    def generar_texto(self, sistema: str, mensaje: str) -> str:
        from google.genai import types

        respuesta = _con_reintentos(lambda: self._cliente.models.generate_content(
            model=config.MODELO_TEXTO,
            contents=mensaje,
            config=types.GenerateContentConfig(system_instruction=sistema, temperature=0.2),
        ))
        return respuesta.text.strip()

    def embeber(self, textos: list[str], es_consulta: bool) -> list[list[float]]:
        from google.genai import types

        tarea = "RETRIEVAL_QUERY" if es_consulta else "RETRIEVAL_DOCUMENT"
        respuesta = _con_reintentos(lambda: self._cliente.models.embed_content(
            model=config.MODELO_EMBEDDINGS,
            contents=textos,
            config=types.EmbedContentConfig(task_type=tarea),
        ))
        return [e.values for e in respuesta.embeddings]
