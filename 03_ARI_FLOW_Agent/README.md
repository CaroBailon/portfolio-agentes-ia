# Proyecto 03: Agente ARI FLOW (Automatización de Soporte al Cliente)

📌 **1. Entorno y Objetivo Principal**

*   **Plataforma de Automatización:** Make (Integromat).
*   **Servicios Integrados:** Gmail, Google Drive, Google Gemini 3.6 Flash.
*   **Técnicas aplicadas:** Automatización de flujos de trabajo (Workflow Automation), Enrutamiento Condicional, RAG (Retrieval-Augmented Generation) y Clasificación de Textos.
*   **Objetivo del Agente (ARI FLOW):** Reducir drásticamente los tiempos de respuesta del equipo de soporte de ARI Consulting. El agente clasifica automáticamente los correos entrantes: responde de manera autónoma a las consultas sobre Oracle Cloud Applications basándose en una base de conocimientos, y deriva las consultas generales o administrativas a un equipo humano.

🏗️ **2. Arquitectura del Flujo (Pipeline de Nodos)**

El escenario fue construido en Make siguiendo una arquitectura de clasificación y derivación inteligente:

1.  **Ingesta (Gmail - Watch Emails):** El sistema monitorea la bandeja de entrada, procesando un límite de 5 correos no leídos por ciclo.
2.  **Clasificación (Gemini AI):** Un nodo de IA evalúa el Asunto (`subject`) y Cuerpo (`snippet`) del correo. Mediante un prompt estricto, actúa como especialista Oracle y devuelve un booleano (`SI` o `NO`) dependiendo de si la consulta trata sobre Oracle HCM, ERP, SCM, CX, etc.
3.  **Enrutador (Make Router):** Divide el flujo de trabajo en dos caminos basados en la respuesta del clasificador.

⚙️ **3. Rutas de Ejecución y Lógica RAG**

**Ruta A: Consultas Oracle (Clasificación = SI)**
*   **Extracción de Conocimiento:** Se conecta a Google Drive para descargar y leer el archivo `Base de Conocimientos Apps Oracle ESP.txt`. Se optó por formato `.txt` para optimizar recursos y latencia.
*   **Generación de Respuesta (Gemini AI):** Mediante RAG, se inyecta el contenido de la base de conocimiento junto con la duda del cliente. El System Prompt asegura que la IA responda en español, lenguaje de negocio, cite fuentes, respete un límite de 4 párrafos y formatee la salida en HTML para legibilidad en el correo.
*   **Acción:** Gmail envía la respuesta al cliente y mueve el correo original a la etiqueta/carpeta `ARI Flow`.

**Ruta B: Consultas Generales (Clasificación = NO / Fallback)**
*   **Acción:** Gmail mueve automáticamente el correo a la etiqueta/carpeta `Help Desk Human` para su revisión manual, evitando alucinaciones o respuestas erróneas de la IA en temas no documentados.

🎥 **4. Demostración y Entregables**

*(Por estrictas políticas de privacidad y protección de datos, no se exponen capturas del buzón de correo electrónico real utilizado en los tests de validación).*

*   **Template Público en Make:**  
    La arquitectura del pipeline puede explorarse de forma interactiva directamente en la plataforma:
    *   ▶️ [Ver Escenario Interactivo de ARI Flow](https://us2.make.com/public/shared-scenario/Na1q5dCZWHq/ari-flow-inmersion)

*   **Código Fuente del Escenario (Blueprint):**  
    El escenario completo ha sido exportado como código fuente en formato JSON. Puede ser importado, auditado e iterado en cualquier entorno de trabajo de Make.
    *   ⚙️ [Descargar blueprint.json](./blueprint.json)
    
*   **Base de Conocimiento (RAG):**
    *   📄 [Base de Conocimientos Apps Oracle ESP.txt](./Base_de_Conocimientos_Apps_Oracle_ESP.txt)
