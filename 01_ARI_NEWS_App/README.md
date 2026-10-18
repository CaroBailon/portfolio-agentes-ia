# Proyecto 01: ARI NEWS App (Panel de Inteligencia de Negocios)

## 📌 1. Entorno y Objetivo Principal
- **Plataforma:** Google Opal (Plataforma Low-Code para agentes IA).
- **Objetivo del Agente (ARI NEWS):** Construir un agente de respuesta inteligente que genere un panel web de inteligencia de negocios, extrayendo y filtrando 3 noticias relevantes en tiempo real basadas en tres variables de entrada del usuario (Sector, Región y Fecha).

## 🏗️ 2. Arquitectura del Pipeline y System Prompts

### Iteración 1: Prompt Inicial (Manejo de Errores)
Se probó un prompt único que falló al devolver links rotos (Error 404) y no identificar correctamente la fuente original.
> **Prompt Inicial (Descartado):** "Crea una app funcional con 3 inputs para el usuario: Sector, Región y Fecha. Utiliza los inputs para buscar 3 noticias relevantes y filtrar los resultados. Muestra las noticias en cards que contengan: Título, Fuente, Fecha, Resumen y Link original."

### Iteración 2: Arquitectura Multi-Agente (Solución Implementada)
Para resolver el problema de las URLs y mejorar el diseño, se estructuró una arquitectura de 4 nodos especializados:

#### 🔹 Nodo 1: Buscador de Noticias
- **Agente:** `text_generation_agent` (con anclaje de búsqueda web).
- **Objetivo:** Investigar en tiempo real y anclar la búsqueda temporalmente.
- **System Prompt:**
  
  ```text
  Objetivo: Usa el text_generation_agent con anclaje de búsqueda para realizar una investigación en la web en tiempo real sobre las 3 noticias más relevantes y recientes relacionadas con el sector y la región especificados.

  Anclaje Temporal y Actualización: DEBES filtrar y restringir rigurosamente tu búsqueda y los resultados a noticias publicadas A PARTIR DE Y DESPUÉS de la fecha especificada por el usuario. No muestres noticias desactualizadas, a menos que encajen estrictamente dentro de la línea de tiempo solicitada por el usuario.

  Validación Inicial de Links: Extrae exactamente el link real de donde se encontró la noticia. Tienes prohibido alucinar o inventar URLs. Extrae 3 noticias distintas con sus respectivas URLs de origen.

  Requisito de Idioma: Todo el contenido generado, títulos, resúmenes y textos de salida deben estar escritos íntegramente en español.
  ```

#### 🔹 Nodo 2: Control de Calidad
- **Objetivo:** Formateador de Datos. Sanitizar los links rotos convirtiéndolos en URLs de búsqueda de Google seguras usando slugs.
- **System Prompt:**

  ```text
  Objetivo: Actuar como un Formateador de Datos. Tu misión es tomar las 3 noticias entregadas en el nodo anterior, mantener sus títulos y resúmenes intactos, y generar para cada una de ellas un link de búsqueda de Google seguro y funcional.

  Regla de Construcción del Link de Google:
  Para cada ítem, toma el Título de la noticia. Convierte ese Título en un slug de búsqueda: transforma el texto en minúsculas, elimina todos los acentos, puntuaciones, caracteres especiales y reemplaza todos los espacios por guiones (-).
  Arma la URL concatenando el prefijo base con el slug generado: [https://www.google.com/search?q=](https://www.google.com/search?q=) + [slug-del-titulo]
  ```

#### 🔹 Nodo 3: Creador de Imágenes
- **Agente:** `nano banana` (16:9).
- **Objetivo:** Generador Visual para crear un encabezado ("Hero") corporativo abstracto sin texto.
- **System Prompt:**
  
  ```text
  Genera una imagen profesional de alta calidad para un encabezado web premium que refleje una estética sofisticada. Genera exactamente una imagen. La imagen no puede tener texto. Solo imagen.
  
  El estilo visual debe ser conceptual, abstracto y minimalista... Usa una paleta de colores limpia y sofisticada (blanco puro, negro carbón profundo y toques sutiles de plata). La composición debe ser un paisaje horizontal amplio, optimizado para una sección principal de la web.
  ```

#### 🔹 Nodo 4: Creador de Página Web (Output)
- **Objetivo:** Integrar los resultados de los nodos anteriores en un panel web limpio usando HTML y CSS embebido.
- **System Prompts (Layout y Ajustes Avanzados):**
  
  ```text
  Crea una página web en HTML para el ARI NEWS que funcione como un panel de inteligencia de noticias. 
  Encabezado: Muestra "ARI NEWS" en la parte superior izquierda en destaque.
  Sección Principal (Hero): Muestra la imagen conceptual en ancho completo.
  Feed de Noticias: Arma 3 bloques verticales... Alterna los fondos de los bloques (#FFFFFF y #F9F9F9). Cada bloque debe iniciar con un número secuencial ("01 / 03").
  Obligatoriedad del Idioma (español): Todas las etiquetas de interfaz DEBEN mostrarse íntegramente en español.
  
  [Ajustes Avanzados - Restricciones Técnicas CSP]
  Eres un Desarrollador Web IA especializado. Tu función es generar un único documento HTML autónomo y funcional para renderización en un iframe.
  Estética: Minimalismo institucional riguroso. Prohibidas las esquinas redondeadas (border-radius: 0).
  CSS Interno: Escribe CSS puro y responsivo embebido exclusivamente en una etiqueta <style>. Está PROHIBIDO importar frameworks externos vía CDN o scripts de terceros. Devuelve SOLO el bloque de código raw comenzando con <html> y terminando con </html>.
  ```

## 📸 Demostración Visual y Funcionamiento

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/abb8faf5-7b8b-4659-91dc-093be5ded9af" alt="ARI1" width="100%" />
      <br><em>Paso 1</em>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/d2c772b7-fd04-4abc-981e-a98016bea250" alt="ARI2" width="100%" />
      <br><em>Paso 2</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/4e9c9226-ff7c-4c0a-8eda-ed39c66b14ae" alt="ARI3" width="100%" />
      <br><em>Paso 3</em>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/a778bdfd-5e8d-456a-8f4f-b6c1de93be46" alt="ARI4" width="100%" />
      <br><em>Paso 4</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/71dae1b0-a968-4993-8a8d-b805a5fb4b6e" alt="ARI5" width="100%" />
      <br><em>Paso 5</em>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/418d4ea4-98ee-4034-9921-17c2337cf012" alt="ARI6" width="100%" />
      <br><em>Resultado Final</em>
    </td>
  </tr>
</table>

> 🎥 **[Ver demostración en video de la App (YouTube)](https://youtu.be/BsHmmy3sKJo)**
