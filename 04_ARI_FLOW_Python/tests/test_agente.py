"""Pruebas del circuito completo con modelos simulados: no usan la API de Gemini.

Verifican el cableado (fragmentar, indexar, recuperar, aplicar las reglas de ruta, el
webhook), no la calidad del modelo. La calidad se mide con evaluacion/evaluar.py.

    pytest -q
"""

import hashlib
import math
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ari_flow import api, config  # noqa: E402
from ari_flow.agente import Agente, Correo  # noqa: E402
from ari_flow.conocimiento import BaseVectorial, fragmentar  # noqa: E402

TEXTO_BASE = config.RUTA_BASE.read_text(encoding="utf-8")


class EmbeddingsSimulados:
    """Bolsa de palabras con hashing: parecido léxico, suficiente para probar la búsqueda."""

    def __init__(self):
        self.llamadas = 0

    def embeber(self, textos, es_consulta):
        self.llamadas += 1
        vectores = []
        for t in textos:
            t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
            v = [0.0] * 256
            for palabra in re.findall(r"[a-z]{4,}", t):
                v[int(hashlib.md5(palabra.encode()).hexdigest(), 16) % 256] += 1
            norma = math.sqrt(sum(x * x for x in v)) or 1
            vectores.append([x / norma for x in v])
        return vectores


class ModeloSimulado:
    """Devuelve la decisión que se le indique y registra qué se le pidió."""

    def __init__(self, decision):
        self.decision = decision
        self.textos_pedidos = 0

    def generar_json(self, sistema, mensaje, esquema):
        return dict(self.decision)

    def generar_texto(self, sistema, mensaje):
        self.textos_pedidos += 1
        return "<p>Sí, con Incentive Compensation (Fuente: 2.4).</p>"


DECISION_IA = {"tipo": "oracle_sales", "cubierta_por_base": True, "pide_algo_administrativo": False,
               "fragmentos_relevantes": ["2.4-2", "9.9-9"], "ruta": "IA", "motivo": "Está en 2.4"}


@pytest.fixture
def base():
    return BaseVectorial(config.RUTA_BASE, EmbeddingsSimulados(), ruta_chroma=None)


def test_fragmentar_respeta_secciones():
    fragmentos = fragmentar(TEXTO_BASE)
    ids = {f.id for f in fragmentos}
    assert len(fragmentos) >= 20
    assert "2.4-2" in ids
    comisiones = next(f for f in fragmentos if f.id == "2.4-2")
    assert "Incentive Compensation" in comisiones.texto
    assert comisiones.seccion.startswith("2.4.")
    assert not any(set(f.texto) == {"_"} or f.texto.startswith("﻿") for f in fragmentos)


def test_busqueda_encuentra_la_seccion_correcta(base):
    assert len(base) == len(fragmentar(TEXTO_BASE))
    resultados = base.buscar("calcular comisiones de ventas y bonificaciones del equipo", k=3)
    assert len(resultados) == 3
    assert resultados[0][0].id == "2.4-2"


def test_indice_persistente_no_se_reconstruye(tmp_path):
    emb = EmbeddingsSimulados()
    BaseVectorial(config.RUTA_BASE, emb, tmp_path)
    llamadas_al_crear = emb.llamadas
    BaseVectorial(config.RUTA_BASE, emb, tmp_path)
    assert emb.llamadas == llamadas_al_crear  # la segunda vez no vuelve a embeber la base


def test_responde_si_la_base_alcanza_y_filtra_fuentes_inventadas(base):
    modelo = ModeloSimulado(DECISION_IA)
    r = Agente(base, modelo).procesar(Correo("a@b.com", "Comisiones", "¿Calcula comisiones de ventas?"))
    assert r.ruta == "IA" and r.carpeta == "ARI Flow"
    assert r.respuesta_html and modelo.textos_pedidos == 1
    assert r.fuentes == ["2.4-2"]  # "9.9-9" no fue recuperado: se descarta


@pytest.mark.parametrize("cambio", [
    {"pide_algo_administrativo": True},    # consulta mixta
    {"cubierta_por_base": False},          # Oracle Sales, pero la base no lo tiene
    {"tipo": "oracle_otro_modulo"},        # Oracle HCM, ERP o SCM
])
def test_las_reglas_en_codigo_ganan_al_modelo(base, cambio):
    modelo = ModeloSimulado({**DECISION_IA, **cambio})  # el modelo sigue diciendo "IA"
    r = Agente(base, modelo).procesar(Correo("a@b.com", "Consulta", "Texto"))
    assert r.ruta == "HUMANO" and r.carpeta == "Help Desk Human"
    assert r.respuesta_html is None and modelo.textos_pedidos == 0


def test_webhook(base, monkeypatch):
    api.app.dependency_overrides[api.obtener_agente] = lambda: Agente(base, ModeloSimulado(DECISION_IA))
    cliente = TestClient(api.app)
    correo = {"remitente": "a@b.com", "asunto": "Comisiones", "cuerpo": "¿Calcula comisiones?"}
    try:
        assert cliente.get("/health").json() == {"estado": "ok"}
        r = cliente.post("/webhook/correo", json=correo)
        assert r.status_code == 200 and r.json()["ruta"] == "IA"
        assert cliente.post("/webhook/correo", json={**correo, "asunto": ""}).status_code == 422

        monkeypatch.setattr(config, "WEBHOOK_TOKEN", "secreto")
        assert cliente.post("/webhook/correo", json=correo).status_code == 401
        ok = cliente.post("/webhook/correo", json=correo, headers={"X-Webhook-Token": "secreto"})
        assert ok.status_code == 200
    finally:
        api.app.dependency_overrides.clear()


def test_evaluacion_completa_con_modelo_simulado(base, capsys):
    from evaluacion import evaluar

    casos = pd.read_csv(config.RUTA_CASOS)
    assert len(casos) == 30
    df = evaluar.correr(Agente(base, ModeloSimulado(DECISION_IA)), casos.head(3), pausa=0)
    evaluar.reportar(df)
    salida = capsys.readouterr().out
    assert "Exactitud del enrutamiento" in salida
    assert set(df["ruta_obtenida"]) == {"IA"}
