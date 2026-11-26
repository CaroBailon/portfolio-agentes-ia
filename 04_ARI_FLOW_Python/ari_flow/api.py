"""Webhook HTTP del agente.

Cualquier sistema que reciba correos (Make, n8n, un script con la API de Gmail) le manda el
correo a POST /webhook/correo y recibe la ruta, la carpeta y, si corresponde, la respuesta.
El envío del mail queda del lado de quien llama: la API decide y redacta, no toca el buzón.

    uvicorn ari_flow.api:app --reload      # y abrir http://127.0.0.1:8000/docs
"""

from functools import lru_cache

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import config
from .agente import Agente, Correo
from .conocimiento import BaseVectorial

app = FastAPI(
    title="ARI FLOW",
    description="Triage de correos de soporte con RAG: responde lo que la base cubre y deriva el resto.",
    version="1.0.0",
)


class CorreoEntrada(BaseModel):
    remitente: str = Field(..., examples=["cliente@empresa.com"])
    asunto: str = Field(..., min_length=1, max_length=300, examples=["Lead scoring en Oracle Sales"])
    cuerpo: str = Field(..., min_length=1, max_length=20_000,
                        examples=["¿Oracle Sales puede priorizar los leads según su probabilidad de compra?"])


class ResultadoSalida(BaseModel):
    ruta: str = Field(..., description="IA: se responde automáticamente. HUMANO: se deriva.")
    carpeta: str
    motivo: str
    tipo: str
    respuesta_html: str | None
    fuentes: list[str]
    similitud_max: float


@lru_cache
def obtener_agente() -> Agente:
    from .llm import Gemini

    gemini = Gemini()
    base = BaseVectorial(config.RUTA_BASE, gemini, config.RUTA_CHROMA)
    return Agente(base, gemini, config.TOP_K)


def verificar_token(x_webhook_token: str | None = Header(default=None)) -> None:
    if config.WEBHOOK_TOKEN and x_webhook_token != config.WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Token de webhook inválido o ausente.")


@app.get("/health")
def health() -> dict:
    return {"estado": "ok"}


@app.post("/webhook/correo", response_model=ResultadoSalida, dependencies=[Depends(verificar_token)])
def recibir_correo(correo: CorreoEntrada, agente: Agente = Depends(obtener_agente)) -> dict:
    # Endpoint `def` y no `async def`: las llamadas al modelo son bloqueantes (SDK sincrónico),
    # así FastAPI las corre en su pool de hilos y no frena a los demás pedidos.
    return agente.procesar(Correo(**correo.model_dump())).a_dict()
