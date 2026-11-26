"""Corre los 30 correos de prueba por el agente y mide el enrutamiento.

Usa el mismo casos_de_prueba.csv que la versión en Make, así las dos se comparan sobre los
mismos correos. Guarda cada resultado en resultados.csv para revisar las respuestas a mano.

    python evaluacion/evaluar.py              # los 30 casos
    python evaluacion/evaluar.py --pausa 7    # más lento, para el límite de la capa gratuita
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ari_flow import config  # noqa: E402
from ari_flow.agente import Agente, Correo  # noqa: E402
from ari_flow.conocimiento import BaseVectorial  # noqa: E402

SALIDA = Path(__file__).with_name("resultados.csv")


def correr(agente: Agente, casos: pd.DataFrame, pausa: float) -> pd.DataFrame:
    filas = []
    for i, caso in enumerate(casos.itertuples(), start=1):
        r = agente.procesar(Correo("prueba@ejemplo.com", caso.asunto, caso.cuerpo))
        filas.append({
            "id": caso.id, "grupo": caso.grupo, "asunto": caso.asunto,
            "ruta_esperada": caso.ruta_esperada, "ruta_obtenida": r.ruta,
            "tipo": r.tipo, "motivo": r.motivo, "fuentes": " ".join(r.fuentes),
            "similitud_max": r.similitud_max,
            "cita_fuente": "SI" if r.respuesta_html and "Fuente" in r.respuesta_html else
                           ("NO" if r.respuesta_html else ""),
            "respuesta_correcta": "",  # se completa a mano leyendo respuesta_html
            "respuesta_html": r.respuesta_html or "",
        })
        print(f"  [{i:2}/{len(casos)}] #{caso.id:<2} {r.ruta:<6} {caso.asunto}")
        if pausa and i < len(casos):
            time.sleep(pausa)
    return pd.DataFrame(filas)


def reportar(df: pd.DataFrame) -> None:
    ok = df["ruta_esperada"].str.upper() == df["ruta_obtenida"].str.upper()
    print(f"\n1. Exactitud del enrutamiento: {ok.mean():.0%} ({ok.sum()} de {len(df)})")
    print(pd.crosstab(df["ruta_esperada"], df["ruta_obtenida"],
                      rownames=["esperada"], colnames=["obtenida"]).to_string())

    print("\n2. Exactitud por grupo")
    print(df.assign(ok=ok).groupby("grupo")["ok"].agg(["mean", "size"])
            .rename(columns={"mean": "exactitud", "size": "casos"})
            .to_string(formatters={"exactitud": "{:.0%}".format}))

    ia = df[df["ruta_obtenida"] == "IA"]
    if len(ia):
        print(f"\n3. Respuestas automáticas: {len(ia)}. Citan la fuente: {(ia['cita_fuente'] == 'SI').mean():.0%}")

    riesgo = df[(df["ruta_esperada"] == "HUMANO") & (df["ruta_obtenida"] == "IA")]
    print(f"\n4. Respondió cuando debía derivar: {len(riesgo)}")
    for r in riesgo.itertuples():
        print(f"   #{r.id} [{r.grupo}] {r.asunto}: {r.motivo}")

    perdidas = df[(df["ruta_esperada"] == "IA") & (df["ruta_obtenida"] == "HUMANO")]
    print(f"\n5. Derivó cuando podía responder: {len(perdidas)}")
    for r in perdidas.itertuples():
        print(f"   #{r.id} [{r.grupo}] {r.asunto}: {r.motivo}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pausa", type=float, default=4.0, help="segundos entre correos")
    args = parser.parse_args()

    from ari_flow.llm import Gemini

    gemini = Gemini()
    base = BaseVectorial(config.RUTA_BASE, gemini, config.RUTA_CHROMA)
    casos = pd.read_csv(config.RUTA_CASOS)
    print(f"Base: {len(base)} fragmentos. Casos: {len(casos)}. Modelo: {config.MODELO_TEXTO}\n")

    df = correr(Agente(base, gemini, config.TOP_K), casos, args.pausa)
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    reportar(df)
    print(f"\nDetalle y respuestas en {SALIDA.name}. Completá respuesta_correcta (si/parcial/no).")


if __name__ == "__main__":
    main()
