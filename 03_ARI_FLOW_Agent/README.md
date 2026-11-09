# Proyecto 03: Agente ARI FLOW (Automatización de Soporte al Cliente)

📌 **1. Entorno y Objetivo Principal**

*   **Plataforma de Automatización:** Make (Integromat).
*   **Servicios Integrados:** Gmail, Google Drive, Google Gemini 3.6 Flash.
*   **Técnicas aplicadas:** Automatización de flujos de trabajo (Workflow Automation), Enrutamiento Condicional, RAG (Retrieval-Augmented Generation) y Clasificación de Textos.
*   **Objetivo del Agente (ARI FLOW):** Reducir los tiempos de respuesta del equipo de soporte de ARI Consulting. El agente clasifica automáticamente los correos entrantes: responde de manera autónoma a las consultas sobre Oracle Cloud Applications basándose en una base de conocimientos, y deriva las consultas generales o administrativas a un equipo humano.

🏗️ **2. Arquitectura del Flujo (Pipeline de Nodos)**

El escenario fue construido en Make siguiendo una arquitectura de clasificación y derivación inteligente:

1.  **Ingesta (Gmail - Watch Emails):** El sistema monitorea la bandeja de entrada, procesando un límite de 5 correos no leídos por ciclo.
2.  **Clasificación (Gemini AI):** Un nodo de IA evalúa el Asunto (`subject`) y Cuerpo (`snippet`) del correo. Mediante un prompt estricto, actúa como especialista Oracle y devuelve un booleano (`SI` o `NO`) dependiendo de si la consulta trata sobre Oracle HCM, ERP, SCM, CX, etc.
3.  **Enrutador (Make Router):** Divide el flujo de trabajo en dos caminos basados en la respuesta del clasificador.

⚙️ **3. Rutas de Ejecución y Lógica RAG**

**Ruta A: Consultas Oracle (Clasificación = SI)**
*   **Extracción de Conocimiento:** Se conecta a Google Drive para descargar y leer el archivo [`base_conocimiento_oracle_sales.txt`](./base_conocimiento_oracle_sales.txt), que cubre Oracle Fusion Cloud Sales. Se optó por formato `.txt` para optimizar recursos y latencia.
*   **Generación de Respuesta (Gemini AI):** Mediante RAG, se inyecta el contenido de la base de conocimiento junto con la duda del cliente. El System Prompt asegura que la IA responda en español, lenguaje de negocio, cite fuentes, respete un límite de 4 párrafos y formatee la salida en HTML para legibilidad en el correo.
*   **Acción:** Gmail envía la respuesta al cliente y mueve el correo original a la etiqueta/carpeta `ARI Flow`.

**Ruta B: Consultas Generales (Clasificación = NO / Fallback)**
*   **Acción:** Gmail mueve automáticamente el correo a la etiqueta/carpeta `Help Desk Human` para su revisión manual, para que la IA no responda sobre temas que no están documentados.

🎥 **4. Demostración y Entregables**

*(Por estrictas políticas de privacidad y protección de datos, no se exponen capturas del buzón de correo electrónico real utilizado en los tests de validación).*

*   **Template Público en Make:**  
    La arquitectura del pipeline puede explorarse de forma interactiva directamente en la plataforma:
    *   ▶️ [Ver Escenario Interactivo de ARI Flow](https://us2.make.com/public/shared-scenario/Na1q5dCZWHq/ari-flow-inmersion)

*   **Código Fuente del Escenario (Blueprint):**  
    El escenario completo ha sido exportado como código fuente en formato JSON. Puede ser importado, auditado e iterado en cualquier entorno de trabajo de Make.
    *   ⚙️ [Ver blueprint.json](./blueprint.json)
    
*   **Base de Conocimiento (RAG):**
    *   📄 [base_conocimiento_oracle_sales.txt](./base_conocimiento_oracle_sales.txt)

📊 **5. Evaluación**

La carpeta [`evaluacion/`](./evaluacion) tiene un set de **30 correos de prueba** etiquetados con la ruta esperada, en cuatro grupos:

| Grupo | Casos | Ruta esperada |
|---|---|---|
| Oracle Sales (cubierto por la base) | 12 | IA |
| Oracle HCM, ERP o SCM (fuera de la base) | 6 | Persona |
| Administrativos y generales | 8 | Persona |
| Ambiguos (otro proveedor, inglés, consultas mixtas) | 4 | Según el caso |

**Cómo correrla:** enviar cada correo al buzón que vigila el escenario, anotar en `casos_de_prueba.csv` a qué carpeta fue (`ruta_obtenida`) y, si respondió la IA, si la respuesta fue correcta y citó la fuente. Después:

```bash
python evaluacion/evaluar.py
```

El script reporta la exactitud del enrutamiento (general y por grupo), la matriz de confusión, la calidad de las respuestas automáticas y la lista de correos que el agente respondió cuando debía derivarlos.

**Hipótesis a verificar:** el clasificador acepta cualquier consulta de Oracle Cloud, pero la base solo cubre Oracle Sales. Si se confirma, la mejora es que el clasificador distinga *"está en la base"* de *"es sobre Oracle"*.
