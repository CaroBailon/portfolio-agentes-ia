"""Base de conocimiento: partirla en fragmentos e indexarla en Chroma.

En Make, el escenario descargaba el .txt entero de Google Drive y lo pegaba en el prompt.
Acá se parte en fragmentos con su sección de origen y solo se le pasan al modelo los más
parecidos al correo. Con una base de 5 KB la diferencia de costo es chica; con un manual de
cientos de páginas, pegar todo deja de ser posible.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import chromadb

from .llm import ModeloEmbeddings

TITULO_SECCION = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$")
NOMBRE_COLECCION = "base_oracle_sales"


@dataclass(frozen=True)
class Fragmento:
    id: str        # p. ej. "2.4-2": sección 2.4, segundo fragmento
    seccion: str   # p. ej. "2.4. Sales Performance Management (SPM)"
    texto: str


def fragmentar(texto: str) -> list[Fragmento]:
    """Un fragmento por viñeta o párrafo, cada uno con el título de su sección."""
    fragmentos: list[Fragmento] = []
    numero, seccion, contador = "0", "Introducción", 0
    for linea in texto.lstrip("﻿").splitlines():
        linea = linea.strip()
        if not linea or set(linea) == {"_"}:
            continue
        coincide = TITULO_SECCION.match(linea)
        if coincide:
            numero, seccion, contador = coincide.group(1), linea, 0
            continue
        contador += 1
        cuerpo = linea.lstrip("*• ").strip()
        fragmentos.append(Fragmento(f"{numero}-{contador}", seccion, cuerpo))
    return fragmentos


class BaseVectorial:
    """Índice de fragmentos en Chroma. Se reconstruye solo si cambia el archivo de la base."""

    def __init__(self, ruta_base: Path, embeddings: ModeloEmbeddings, ruta_chroma: Path | None):
        self._embeddings = embeddings
        cliente = (chromadb.PersistentClient(path=str(ruta_chroma)) if ruta_chroma
                   else chromadb.EphemeralClient())
        texto = Path(ruta_base).read_text(encoding="utf-8")
        huella = hashlib.sha256(texto.encode()).hexdigest()[:16]

        existente = next((c for c in cliente.list_collections() if c.name == NOMBRE_COLECCION), None)
        if existente is not None and (existente.metadata or {}).get("huella") == huella:
            self._coleccion = cliente.get_collection(NOMBRE_COLECCION, embedding_function=None)
            return
        if existente is not None:
            cliente.delete_collection(NOMBRE_COLECCION)

        fragmentos = fragmentar(texto)
        self._coleccion = cliente.create_collection(
            NOMBRE_COLECCION, embedding_function=None,
            metadata={"huella": huella, "hnsw:space": "cosine"})
        # Se embebe "sección + texto": la sección aporta contexto que la viñeta sola no tiene.
        documentos = [f"{f.seccion}\n{f.texto}" for f in fragmentos]
        self._coleccion.add(
            ids=[f.id for f in fragmentos],
            documents=[f.texto for f in fragmentos],
            metadatas=[{"seccion": f.seccion} for f in fragmentos],
            embeddings=self._embeddings.embeber(documentos, es_consulta=False),
        )

    def __len__(self) -> int:
        return self._coleccion.count()

    def buscar(self, consulta: str, k: int) -> list[tuple[Fragmento, float]]:
        """Devuelve los k fragmentos más parecidos con su similitud (1 = idéntico)."""
        vector = self._embeddings.embeber([consulta], es_consulta=True)[0]
        r = self._coleccion.query(query_embeddings=[vector], n_results=k)
        return [
            (Fragmento(i, m["seccion"], d), round(1 - dist, 3))
            for i, d, m, dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])
        ]
