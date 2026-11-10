
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACION DE LA PAGINA
# ==========================================

st.set_page_config(
    page_title="Huella Ecológica del Perú",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 Huella Ecológica del Perú")
st.subheader("Análisis de los componentes de la huella ecológica (2009-2016)")

st.write(
    "Esta sección permite explorar y comparar los componentes "
    "de la huella ecológica en los departamentos del Perú."
)

# ==========================================
# 1. CARGAR LOS DATOS
# ==========================================

@st.cache_data
def cargar_datos():

    ruta = "datos_set/DAG_HuellaEcologica.xlsx"

    df = pd.read_excel(
        ruta,
        sheet_name="2009",
        header=6
    )

    df.columns = df.columns.str.strip()

    return df

try:
    df = cargar_datos()

    st.success("Datos cargados correctamente.")

except Exception as e:
    st.error(f"No se pudo cargar el archivo: {e}")
    st.stop()

# ==========================================
# 2. COMPONENTES AMBIENTALES
# ==========================================

componentes = [
    "Área de Cultivos",
    "Área de Pastoreo",
    "Área de Bosques",
    "Zonas de Pesca",
    "Huella de Carbono",
    "Áreas Urbanas"
]

# Convertir componentes a valores numéricos
for columna in componentes:
    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    )

df["Año"] = pd.to_numeric(df["Año"], errors="coerce")

# ==========================================
# 3. FILTROS DE CONSULTA
# ==========================================

st.markdown("### Filtros de consulta")

col1, col2 = st.columns(2)

with col1:

    años = sorted(df["Año"].dropna().unique())

    año_seleccionado = st.selectbox(
        "Selecciona el año:",
        años,
        index=len(años) - 1
    )

with col2:

    departamentos = sorted(
        df["Ámbito"].dropna().unique()
    )

    departamentos_seleccionados = st.multiselect(
        "Selecciona los departamentos:",
        departamentos,
        default=departamentos
    )

# ==========================================
# 4. FILTRAR LOS DATOS
# ==========================================

df_filtrado = df[
    (df["Año"] == año_seleccionado) &
    (df["Ámbito"].isin(departamentos_seleccionados))
].copy()

# ==========================================
# 5. GRAFICO DE BARRAS APILADAS
# ==========================================

st.markdown("### Componentes de la huella ecológica")

if not df_filtrado.empty:

    df_grafico = df_filtrado.melt(
        id_vars=["Ámbito"],
        value_vars=componentes,
        var_name="Componente",
        value_name="Valor"
    )

    orden = (
        df_filtrado
        .set_index("Ámbito")[componentes]
        .sum(axis=1)
        .sort_values()
        .index.tolist()
    )

    fig = px.bar(
        df_grafico,
        x="Valor",
        y="Ámbito",
        color="Componente",
        orientation="h",
        barmode="stack",
        category_orders={"Ámbito": orden},
        title=f"Huella ecológica por componentes - {int(año_seleccionado)}",
        labels={
            "Valor": "Huella ecológica per cápita",
            "Ámbito": "Departamento",
            "Componente": "Componente ambiental"
        },
        hover_data={"Valor": ":.4f"}
    )

    fig.update_layout(
        height=750,
        template="plotly_white",
        legend_title="Componentes",
        xaxis_title="Valor per cápita",
        yaxis_title="Departamento"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning("Selecciona al menos un departamento.")

# ==========================================
# 6. TABLA DE DATOS
# ==========================================

st.markdown("### Datos utilizados")

if not df_filtrado.empty:

    columnas_tabla = (
        ["Ámbito"] +
        componentes +
        ["Huella Regional Per Capita"]
    )

    st.dataframe(
        df_filtrado[columnas_tabla],
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 7. INFORMACION DEL ANALISIS
# ==========================================

st.markdown("---")

st.caption(
    "Fuente: documentación estadística del Ministerio del Ambiente (MINAM). "
    "Periodo de análisis: 2009-2016."
)
