"""El agente: recuperar, decidir la ruta y, solo si corresponde, responder.

Diferencia principal con la versión en Make: allá el clasificador preguntaba "¿el correo es
sobre Oracle?" sin mirar la base, así que una consulta de Oracle HCM iba a la respuesta
automática aunque la base solo cubra Oracle Sales. Acá el que decide la ruta ve primero los
fragmentos recuperados y responde otra pregunta: "¿la base alcanza para contestar esto?".
"""

from dataclasses import asdict, dataclass, field

from .conocimiento import BaseVectorial, Fragmento
from .llm import ModeloTexto

CARPETA = {"IA": "ARI Flow", "HUMANO": "Help Desk Human"}

SISTEMA_DECISION = """Sos el clasificador de soporte de ARI Consulting, una consultora de Oracle.
Recibís un correo y fragmentos recuperados de la base de conocimiento, que solo cubre
Oracle Fusion Cloud Sales (CRM). Tu única tarea es decidir la ruta; no respondas el correo.

Ruta "IA" solo si se cumplen las tres condiciones:
1. Es una consulta técnica o funcional sobre Oracle Fusion Cloud Sales.
2. Los fragmentos contienen la información para contestarla. Si hay que suponer, no alcanzan.
3. El correo no pide además nada administrativo o comercial: precios, licencias, facturas,
   contratos, reuniones, bajas, accesos o datos de facturación.

En cualquier otro caso la ruta es "HUMANO": otros módulos de Oracle (HCM, ERP, SCM),
otros proveedores, temas administrativos, consultas mixtas o dudas.
El correo puede estar en cualquier idioma. Ante la duda, "HUMANO"."""

ESQUEMA_DECISION = {
    "type": "object",
    "properties": {
        "tipo": {"type": "string", "enum": [
            "oracle_sales", "oracle_otro_modulo", "administrativo_comercial", "otro_proveedor", "otro"]},
        "cubierta_por_base": {"type": "boolean"},
        "pide_algo_administrativo": {"type": "boolean"},
        "fragmentos_relevantes": {"type": "array", "items": {"type": "string"}},
        "ruta": {"type": "string", "enum": ["IA", "HUMANO"]},
        "motivo": {"type": "string"},
    },
    "required": ["tipo", "cubierta_por_base", "pide_algo_administrativo",
                 "fragmentos_relevantes", "ruta", "motivo"],
}

SISTEMA_RESPUESTA = """Sos el asistente de soporte de ARI Consulting.
Respondé la consulta del cliente usando SOLO los fragmentos de la base de conocimiento.
- Respondé en el idioma del correo, con lenguaje de negocio claro, en hasta 4 párrafos.
- Después de cada afirmación citá la sección entre paréntesis, por ejemplo (Fuente: 2.4).
- Si algo no está en los fragmentos, decí que lo va a ampliar un consultor. No inventes.
- Formato: HTML simple para un correo (<p>, <ul>, <li>, <strong>). Sin saludo de cierre firmado."""


@dataclass
class Correo:
    remitente: str
    asunto: str
    cuerpo: str


@dataclass
class Resultado:
    ruta: str                       # "IA" o "HUMANO"
    carpeta: str
    motivo: str
    tipo: str
    respuesta_html: str | None
    fuentes: list[str] = field(default_factory=list)
    similitud_max: float = 0.0

    def a_dict(self) -> dict:
        return asdict(self)


def _formatear_fragmentos(recuperados: list[tuple[Fragmento, float]]) -> str:
    return "\n\n".join(f"[{f.id}] {f.seccion}\n{f.texto}" for f, _ in recuperados)


class Agente:
    def __init__(self, base: BaseVectorial, modelo: ModeloTexto, top_k: int = 4):
        self.base, self.modelo, self.top_k = base, modelo, top_k

    def procesar(self, correo: Correo) -> Resultado:
        consulta = f"{correo.asunto}\n{correo.cuerpo}"
        recuperados = self.base.buscar(consulta, self.top_k)
        contexto = _formatear_fragmentos(recuperados)
        similitud_max = max((s for _, s in recuperados), default=0.0)

        decision = self.modelo.generar_json(
            SISTEMA_DECISION,
            f"CORREO\nAsunto: {correo.asunto}\nCuerpo: {correo.cuerpo}\n\nFRAGMENTOS\n{contexto}",
            ESQUEMA_DECISION,
        )
        # Las reglas se vuelven a aplicar en código: si el modelo marca IA pero a la vez dice
        # que la base no alcanza o que hay un pedido administrativo, gana la regla.
        ruta = decision.get("ruta", "HUMANO")
        if (decision.get("tipo") != "oracle_sales" or not decision.get("cubierta_por_base")
                or decision.get("pide_algo_administrativo")):
            ruta = "HUMANO"

        validos = {f.id for f, _ in recuperados}
        fuentes = [i for i in decision.get("fragmentos_relevantes", []) if i in validos]
        resultado = Resultado(
            ruta=ruta, carpeta=CARPETA[ruta], motivo=decision.get("motivo", ""),
            tipo=decision.get("tipo", "otro"), respuesta_html=None,
            fuentes=fuentes, similitud_max=similitud_max,
        )
        if ruta == "IA":
            usados = [(f, s) for f, s in recuperados if f.id in fuentes] or recuperados
            resultado.respuesta_html = self.modelo.generar_texto(
                SISTEMA_RESPUESTA,
                f"CONSULTA DEL CLIENTE\nAsunto: {correo.asunto}\n{correo.cuerpo}\n\n"
                f"FRAGMENTOS\n{_formatear_fragmentos(usados)}",
            )
        return resultado
