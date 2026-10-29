# 🤖 Ecosistema BPA: Agentes Autónomos con IA Generativa

![Google Opal](https://img.shields.io/badge/Google%20Opal-Low--Code-blue)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-orange)
![Make](https://img.shields.io/badge/Make-Integromat-blueviolet)
![ChatGPT](https://img.shields.io/badge/ChatGPT-Custom%20Instructions-green)

Código fuente y arquitectura de un **Ecosistema Multi-Agente** diseñado para la Automatización de Procesos de Negocio (BPA). 

Este proyecto resuelve cuellos de botella operativos mediante la orquestación de Modelos de Lenguaje (LLMs), arquitecturas RAG (Retrieval-Augmented Generation) y pipelines de automatización, conectando la ejecución técnica con la eficiencia corporativa.

## 🏗️ Arquitectura del Ecosistema

### 📁 [01_ARI_NEWS_App](./01_ARI_NEWS_App) — Panel de Inteligencia de Negocios (BI)
Pipeline orquestado en **Google Opal** estructurado en 4 nodos especializados:
1. **Buscador (Web Grounding):** Extracción de noticias en tiempo real con filtrado temporal estricto.
2. **Control de Calidad (QC):** Sanitización de URLs rotas mediante la conversión de títulos en slugs de búsqueda seguros.
3. **Generador Visual:** Creación de assets corporativos abstractos mediante modelos de imagen (formato 16:9).
4. **Web Creator:** Renderizado del output en un panel HTML autónomo con CSS responsivo embebido (estricto cumplimiento CSP).

### 📁 [02_ARI_DEAL_Agent](./02_ARI_DEAL_Agent) — Motor RAG Comercial
Agente conversacional configurado vía **ChatGPT (Custom Instructions / Meta-prompting)** para la generación automatizada de propuestas comerciales en Word.
* **Ingesta RAG:** Utiliza catálogos PDF y plantillas de la consultora para imponer reglas de negocio (inversión, plazos).
* **Flujo A (Validador):** Ingesta un briefing crudo, mapea 10 campos clave, detecta información faltante y valida alertas de presupuesto antes de accionar.
* **Flujo B (Entrevista):** Construye la propuesta desde cero mediante un formulario conversacional guiado por etapas.

### 📁 [03_ARI_FLOW_Agent](./03_ARI_FLOW_Agent) — Pipeline de Soporte (Triage AI)
Automatización en **Make (Integromat)** que integra Gmail, Google Drive y **Google Gemini 3.6 Flash**.
* **Clasificador Semántico:** Un nodo IA evalúa los correos entrantes y activa un enrutador condicional.
* **Ruta IA (Consultas Técnicas):** Descarga la base de conocimientos (`.txt` para optimizar latencia) y responde en HTML usando inyección RAG.
* **Ruta Humana (Fallback):** Deriva consultas administrativas o fuera de dominio a la etiqueta "Help Desk Human", garantizando una política de *Zero-Hallucination*.

## 🛠️ Stack Tecnológico
* **Plataformas & IA:** Google Opal, API Google Gemini (Flash), ChatGPT Plus.
* **Ingeniería & Orquestación:** Make (Integromat), RAG, Prompt Engineering Avanzado (Meta-prompting, Web Grounding).
* **Frontend:** HTML5, CSS3 puro (código autónomo).

## 🎯 Impacto Operativo (Product Sense)
1. **Inteligencia Competitiva:** ARI NEWS provee monitoreo de mercado validado y listo para consumir.
2. **Estandarización Comercial:** ARI DEAL elimina tiempos manuales de redacción y previene errores humanos en facturación gracias a la validación de reglas de negocio.
3. **Reducción de SLA:** ARI FLOW automatiza el soporte de nivel 1, liberando al equipo humano mediante un triage inteligente y seguro.
