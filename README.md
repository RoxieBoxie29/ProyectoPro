# <div align="center">

# Huella Ecológica Departamental per Cápita del Perú, 2009–2016

### Aplicación web de análisis exploratorio de datos

Proyecto Final de Programación Avanzada

<img src="https://www.fundeen.com/_next/image?url=https%3A%2F%2Fblog.fundeen.com%2Fcontenido%2Fuploads%2F2023%2F08%2FHuellaecologicablog-1024x535.png&w=1080&q=100" alt="Huella ecológica" width="800">
<br>
<sub>Imagen: Fundeen, <a href="https://www.fundeen.com/blog-energias-renovables/huella-ecologica">Huella Ecológica: qué es y cómo se calcula</a></sub>

<br>

**[Acceder a la aplicación web]([PEGAR AQUÍ EL ENLACE DE STREAMLIT CLOUD])**

</div>

---

## Resumen

Este proyecto presenta una aplicación web interactiva para explorar la huella ecológica per cápita de los departamentos del Perú entre 2009 y 2016. La herramienta permite comparar departamentos, analizar su evolución en el tiempo y examinar la contribución de cada componente a la huella total.

## Datos

| Aspecto | Descripción |
|---|---|
| Fuente | Dirección de Información e Investigación Ambiental, Ministerio del Ambiente (DIIA - MINAM) |
| Periodo | 2009 a 2016, un archivo Excel por año |
| Unidad de análisis | 24 departamentos y el total nacional |
| Unidad de medida | Hectáreas globales (Hag) por habitante |
| Componentes | Cultivos, pastoreo, bosques, pesca, carbono y áreas urbanas |

La huella total de cada ámbito corresponde a la suma de sus seis componentes.

## Visualizaciones

| Sección | Descripción |
|---|---|
| Evolución | Variación temporal de la huella por departamento, con el promedio nacional como referencia |
| Ranking | Ordenamiento de los departamentos según su huella en un año determinado |
| Composición | Aporte de cada componente a la huella total |
| Mapa de calor | Comparación simultánea de todos los departamentos y años |
| Datos | Tabla completa con opción de descarga en formato CSV |

El usuario puede filtrar la información por rango de años, departamentos y componente desde la barra lateral.

## Ejecución local

```bash
git clone https://github.com/RoxieBoxie29/ProyectoPro.git
cd ProyectoPro
streamlit run app.py
```

## Contenido del repositorio

- `app.py`: código fuente de la aplicación.
- Archivos Excel `DAG_HuellaEcologica2009` a `DAG_HuellaEcologica2016`: datos de origen.

## Autores

- [Nombre completo 1]
- [Nombre completo 2]

## Información académica

- Curso: Programación Avanzada
- Docente: Dr. John Edgar Vargas Muñoz
- Año: 2026