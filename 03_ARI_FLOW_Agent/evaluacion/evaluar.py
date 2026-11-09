"""Calcula las métricas de ARI Flow a partir de casos_de_prueba.csv completado.

Columnas a completar después de enviar cada correo al buzón de prueba:
  ruta_obtenida       IA | HUMANO   (carpeta a la que Make movió el correo)
  respuesta_correcta  si | parcial | no   (solo para la ruta IA)
  cita_fuente         si | no            (solo para la ruta IA)
"""
from pathlib import Path
import sys

import pandas as pd

archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("casos_de_prueba.csv")
df = pd.read_csv(archivo)
df = df[df["ruta_obtenida"].notna()].copy()
if df.empty:
    sys.exit("Completá la columna ruta_obtenida antes de evaluar.")
for c in ["ruta_esperada", "ruta_obtenida", "respuesta_correcta", "cita_fuente"]:
    df[c] = df[c].astype(str).str.strip().str.upper()

print(f"Casos evaluados: {len(df)}\n")

print("1. Enrutamiento: ¿el correo fue a la carpeta correcta?")
acierto = (df["ruta_esperada"] == df["ruta_obtenida"]).mean()
print(f"   Exactitud: {acierto:.0%}")
print(pd.crosstab(df["ruta_esperada"], df["ruta_obtenida"],
                  rownames=["esperada"], colnames=["obtenida"]).to_string(), "\n")

print("2. Exactitud por grupo")
print(df.assign(ok=df["ruta_esperada"] == df["ruta_obtenida"])
        .groupby("grupo")["ok"].agg(["mean", "size"])
        .rename(columns={"mean": "exactitud", "size": "casos"})
        .to_string(formatters={"exactitud": "{:.0%}".format}), "\n")

ia = df[df["ruta_obtenida"] == "IA"]
if len(ia):
    print(f"3. Calidad de las {len(ia)} respuestas automáticas")
    print(ia["respuesta_correcta"].value_counts(normalize=True)
            .to_string(float_format="{:.0%}".format))
    print(f"   Citan la fuente: {(ia['cita_fuente'] == 'SI').mean():.0%}\n")

riesgo = df[(df["ruta_esperada"] == "HUMANO") & (df["ruta_obtenida"] == "IA")]
print(f"4. Respuestas automáticas que debió atender una persona: {len(riesgo)}")
for _, r in riesgo.iterrows():
    print(f"   #{r['id']} [{r['grupo']}] {r['asunto']}")
