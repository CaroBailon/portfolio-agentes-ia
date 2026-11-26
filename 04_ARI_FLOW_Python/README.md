# Proyecto 04: ARI FLOW en Python

El mismo agente de soporte de [ARI FLOW](../03_ARI_FLOW_Agent), reconstruido en código: base vectorial con **Chroma**, **RAG** con la API de **Gemini**, un **webhook** en **FastAPI** y la misma evaluación de 30 correos para comparar las dos versiones.

`Python` · `Gemini API` · `Chroma` · `RAG` · `FastAPI` · `pytest`

## Qué cambia respecto de la versión en Make

| | ARI FLOW en Make | ARI FLOW en Python |
|---|---|---|
| **Pregunta del clasificador** | "¿El correo es sobre Oracle?" | "¿La base alcanza para contestarlo?" |
| **Qué ve el clasificador** | Solo el correo | El correo **y** los fragmentos recuperados de la base |
| **Base de conocimiento** | El `.txt` entero pegado en el prompt | 24 fragmentos indexados en Chroma; al modelo le llegan los 4 más parecidos |
| **Reglas de derivación** | Dentro del prompt | En el prompt **y** verificadas en código: si el modelo dice "IA" pero marca que la base no alcanza o que hay un pedido administrativo, la ruta pasa a "HUMANO" |
| **Fuentes** | El modelo cita como puede | Cada fragmento tiene un id de sección (`2.4-2`); se descartan los ids que el modelo invente |
| **Entrada** | Gmail (Watch Emails) | Webhook HTTP: lo puede llamar Make, n8n o cualquier sistema |
| **Evaluación** | Manual: mandar 30 mails y anotar a qué carpeta fue cada uno | Un comando: `python evaluacion/evaluar.py` |

**El problema que ataca:** por cómo está planteado el clasificador de Make, una consulta sobre sueldos en Oracle HCM iría a la respuesta automática porque "es sobre Oracle", aunque la base solo cubre Oracle Sales. Es la hipótesis que el set de prueba de la versión en Make quiere verificar. Acá el clasificador recibe los fragmentos recuperados antes de decidir, así que puede ver que ninguno habla de sueldos y derivar el correo.

## Cómo funciona

```
Correo ──► POST /webhook/correo
              │
              ▼
   1. Recuperar   Chroma devuelve los 4 fragmentos más parecidos al correo
              │
              ▼
   2. Decidir     Gemini (salida JSON): tipo de consulta, ¿la base alcanza?,
              │   ¿pide algo administrativo?, fragmentos relevantes, ruta
              │   + reglas en código que pueden pasar la ruta a HUMANO
              │
      ┌───────┴────────┐
      ▼                ▼
   ruta IA          ruta HUMANO
   3. Responder     carpeta "Help Desk Human"
   Gemini redacta en HTML usando solo los fragmentos
   elegidos y cita la sección: (Fuente: 2.4)
```

Clasificar y responder siguen separados, igual que en Make: el modelo que decide la ruta no redacta, y el que redacta solo se llama si la ruta es IA.

## Cómo usarlo

```bash
cd 04_ARI_FLOW_Python
pip install -r requirements.txt
cp .env.example .env        # en Windows: copy .env.example .env
```

Completá `GEMINI_API_KEY` en `.env`. La clave se saca gratis en [Google AI Studio](https://aistudio.google.com/apikey).

**Levantar el webhook:**

```bash
uvicorn ari_flow.api:app --reload
```

Abrir **http://127.0.0.1:8000/docs** y probar `POST /webhook/correo` con un correo:

```json
{
  "remitente": "cliente@empresa.com",
  "asunto": "Cálculo de comisiones",
  "cuerpo": "Necesitamos calcular comisiones y bonos del equipo comercial. ¿Oracle Cloud Sales tiene algo para eso?"
}
```

Devuelve la ruta, la carpeta, el motivo, las fuentes y, si la ruta es IA, la respuesta en HTML. Si definís `WEBHOOK_TOKEN` en `.env`, el webhook exige ese valor en el encabezado `X-Webhook-Token`.

**Conectarlo a Make:** en el escenario original, reemplazar los dos nodos de Gemini por un módulo **HTTP → Make a request** que mande el correo a este webhook, y usar `ruta` en el router. El webhook decide y redacta; el envío y el movimiento de carpetas siguen en Make.

## Evaluación

```bash
python evaluacion/evaluar.py
```

Corre los **mismos 30 correos** de [`03_ARI_FLOW_Agent/evaluacion`](../03_ARI_FLOW_Agent/evaluacion) y reporta:

1. Exactitud del enrutamiento y matriz de confusión
2. Exactitud por grupo (Oracle Sales, otros módulos de Oracle, administrativos, ambiguos)
3. Cuántas respuestas automáticas citan la fuente
4. Correos que respondió cuando debía derivar (el error más caro)
5. Correos que derivó cuando podía responder

Cada resultado queda en `evaluacion/resultados.csv`, con el motivo de la decisión y la respuesta generada. La columna `respuesta_correcta` se completa a mano, leyendo cada respuesta.

La capa gratuita de Gemini limita los pedidos por minuto. Por eso el script espera 4 segundos entre correos (`--pausa` para cambiarlo); los 30 casos tardan unos 3 minutos.

### Resultados

> Pendiente: completar con la salida de `evaluar.py`.

| Grupo | Casos | Ruta esperada | Exactitud |
|---|---|---|---|
| Oracle Sales (cubierto por la base) | 12 | IA | – |
| Oracle HCM, ERP o SCM (fuera de la base) | 6 | Persona | – |
| Administrativos y generales | 8 | Persona | – |
| Ambiguos | 4 | Según el caso | – |
| **Total** | **30** | | **–** |

## Pruebas

```bash
pytest -q
```

Nueve pruebas con modelos simulados, sin llamar a la API: fragmentación de la base, búsqueda en Chroma, que el índice no se reconstruya si la base no cambió, las reglas de derivación (que ganen al modelo cuando se contradice), el filtro de fuentes inventadas y el webhook (validación, token). Prueban el cableado del agente; la calidad de las decisiones se mide con la evaluación.

## Estructura

```
04_ARI_FLOW_Python/
├── ari_flow/
│   ├── config.py         # variables de entorno
│   ├── llm.py            # interfaz del modelo + implementación con Gemini
│   ├── conocimiento.py   # fragmentar la base e indexarla en Chroma
│   ├── agente.py         # recuperar → decidir → responder
│   └── api.py            # webhook FastAPI
├── evaluacion/evaluar.py # los 30 casos de prueba
├── tests/                # pruebas con modelos simulados
├── requirements.txt
└── .env.example
```

El agente depende de una interfaz (`ModeloTexto`, `ModeloEmbeddings`), no de Gemini: cambiar a otro proveedor es escribir una clase nueva en `llm.py`.

## Limitaciones

- La base tiene 24 fragmentos: con una base así de chica, Chroma no es imprescindible. Se usa para que el diseño escale a manuales reales sin cambiar el agente.
- Los resultados de la versión en Make con los 30 casos todavía no están cargados en `casos_de_prueba.csv`, así que por ahora la comparación entre las dos es de diseño, no de resultados. La hipótesis a verificar es que la versión en Python deriva los 6 casos de Oracle HCM, ERP y SCM que la de Make respondería.
- No envía correos ni lee el buzón: eso queda del lado de quien llama al webhook.
