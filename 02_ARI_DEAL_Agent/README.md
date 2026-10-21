# Proyecto 02: Agente ARI DEAL (Generador de Propuestas Comerciales)

📌 **1. Entorno y Objetivo Principal**

*   **Plataforma:** ChatGPT (Proyectos y Skills / Custom Instructions).
*   **Técnicas aplicadas:** Meta-prompting y RAG (Retrieval-Augmented Generation).
*   **Objetivo del Agente (ARI DEAL):** Construir un agente conversacional y generador de documentos que asista a los vendedores de ARI Consulting (consultora ficticia de Oracle) en la creación de propuestas comerciales estandarizadas en formato Word (`.docx`). El objetivo es automatizar la redacción y maquetación para que el equipo comercial maximice su tiempo en la atención al cliente.

🏗️ **2. Arquitectura de Datos y Base de Conocimiento (RAG)**

El agente utiliza una base de conocimiento anclada (archivos de referencia) para garantizar que las salidas cumplan estrictamente con las reglas de negocio:
*   `Proposta-Comercial-ARI-CONSULTING.docx`: Plantilla oficial con la estructura de 5 secciones.
*   `Catalogo-Servicos-2026-ARI-CONSULTING.pdf`: Reglas inviolables, servicios vigentes, rangos de inversión y plazos.
*   `brand-book_es.json`: Sistema visual, paleta de colores y tipografía de la marca.
*   Archivos PDF de ejemplo (Ej: *Banco-Central-Sul* y *Logistica-Norte*) para calibrar el tono y nivel de detalle.

⚙️ **3. Flujo de Trabajo y Lógica del Sistema**

El agente ARI DEAL está programado con un *System Prompt* robusto que maneja dos flujos de interacción principales:

*   **Flujo A (Validador de Briefing):** Ingesta de un archivo previo (ej. `.txt` o `.docx`). El agente extrae la información, mapea 10 campos obligatorios, identifica opcionales, aplica reglas de validación (ej. alertas de presupuesto o descuentos) y solicita únicamente la información faltante.
*   **Flujo B (Formulario Guiado):** Entrevista interactiva de 5 etapas para construir la propuesta desde cero de forma conversacional.

🚀 **4. Escalabilidad: Creación de Skill Reutilizable**

Para evitar la ineficiencia de copiar y pegar el System Prompt repetidamente, la arquitectura evolucionó a la creación de una **Skill** nativa.
*   **Implementación:** Se encapsuló toda la lógica, mapeo de campos, reglas de negocio y flujos de entrada en una habilidad invocable mediante el comando `$Propuestas ARI Consulting`.
*   **Testing:** Se validó el funcionamiento integral ingestando el archivo de prueba `briefing-prueba-vetria-empaques_es`, demostrando la correcta lectura, validación de reglas de negocio, resumen ejecutivo y generación exitosa del entregable final formateado.

🎥 **5. Demostración y Entregables Generados**

Para evidenciar el funcionamiento end-to-end del agente y de la Skill, se documentaron los tests realizados y los documentos generados:

*   **Videos de Testing:** Muestran la interacción en tiempo real con el agente, la validación de alertas y la ejecución exitosa de la Skill en sus diferentes flujos.
    *   ▶️ [Test Flujo A - Validación de Briefing (Ver en YouTube)](https://youtu.be/KLZalpNxidE)
    *   ▶️ [Test Flujo B - Formulario Guiado (Ver en YouTube)](https://youtu.be/0z4w8qlBXTY)

*   **Documentos Generados:** Archivos creados exitosamente durante las pruebas, formateados en Word y listos para que el equipo comercial los envíe al cliente.
    *   📄 [Propuesta-872-2026-Banco-Central-del-Sur-ARI-CONSULTING.docx](./Propuesta-872-2026-Banco-Central-del-Sur-ARI-CONSULTING.docx)
    *   📄 [Propuesta-982-2026-Vetria-Empaques-Industriales-ARI-CONSULTING.docx](./Propuesta-982-2026-Vetria-Empaques-Industriales-ARI-CONSULTING.docx)
