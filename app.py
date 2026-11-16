import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# set_page_config va una sola vez y antes de cualquier otro comando de Streamlit
st.set_page_config(
    page_title="Huella ecológica por departamento",
    page_icon="🌎",
    layout="wide",
)


@st.cache_data
def cargar_datos():
    df = pd.read_excel("datos_set/DAG_HuellaEcologica.xlsx", header=6)
    df.columns = df.columns.astype(str).str.strip()

    df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
    df["Ámbito"] = df["Ámbito"].astype(str).str.strip()
    df = df.dropna(subset=["Ámbito", "Año"])
    df["Año"] = df["Año"].astype(int)
    return df


df = cargar_datos()

st.title("Huella ecológica por departamento (2009 - 2016)")

tab_pesca, tab_bosques = st.tabs(["🐟 Zonas de Pesca", "🌳 Área de Bosques"])

# ---------------------------------------------------------------
# PESTAÑA 1: Zonas de Pesca (gráfico de líneas)
# ---------------------------------------------------------------
with tab_pesca:
    st.subheader("Zonas de Pesca por departamento")

    pesca = df.pivot(index="Año", columns="Ámbito", values="Zonas de Pesca")
    pesca.index = pesca.index.astype(str)

    departamentos = list(pesca.columns)
    seleccion = st.multiselect("Departamentos", departamentos, default=departamentos)

    if len(seleccion) == 0:
        st.write("Elige al menos un departamento.")
    else:
        st.line_chart(pesca[seleccion])

        st.subheader("Valores por año")
        st.dataframe(pesca[seleccion])

# ---------------------------------------------------------------
# PESTAÑA 2: Área de Bosques (ranking por año)
# ---------------------------------------------------------------
with tab_bosques:
    st.subheader("Área de Bosques por departamento")
    st.write(
        "Selecciona un año para comparar el indicador Área de Bosques "
        "entre los departamentos del Perú."
    )

    anios = sorted(df["Año"].unique())
    anio = st.selectbox("Selecciona el año:", anios, index=0)

    datos = df[df["Año"] == anio].copy()
    datos["Área de Bosques"] = pd.to_numeric(datos["Área de Bosques"], errors="coerce")
    datos = datos.dropna(subset=["Área de Bosques"])
    datos = datos.sort_values(by="Área de Bosques", ascending=False)

    st.markdown(f"### Resultados del año {anio}")

    mayor = datos.iloc[0]
    menor = datos.iloc[-1]
    promedio = datos["Área de Bosques"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Mayor valor", mayor["Ámbito"])
    col2.metric("Menor valor", menor["Ámbito"])
    col3.metric("Promedio de los departamentos", f"{promedio:.4f}")

    fig = go.Figure()

    for _, fila in datos.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[0, fila["Área de Bosques"]],
                y=[fila["Ámbito"], fila["Ámbito"]],
                mode="lines",
                line=dict(color="#B7DCCB", width=3),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=datos["Área de Bosques"],
            y=datos["Ámbito"],
            mode="markers+text",
            text=datos["Área de Bosques"].map(lambda valor: f"{valor:.3f}"),
            textposition="middle right",
            marker=dict(size=11, color="#16866B"),
            hovertemplate="<b>%{y}</b><br>Área de Bosques: %{x:.6f}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=f"Área de Bosques por departamento - {anio}",
        height=750,
        template="plotly_white",
        xaxis_title="Valor del indicador Área de Bosques",
        yaxis_title="Departamento",
        yaxis=dict(
            categoryorder="array",
            categoryarray=datos["Ámbito"].tolist(),
            autorange="reversed",
        ),
        margin=dict(l=20, r=70, t=70, b=40),
    )

    st.plotly_chart(fig, width="stretch")

    st.markdown("### Datos del gráfico")

    tabla = datos[["Ámbito", "Área de Bosques"]].copy()
    tabla["Área de Bosques"] = tabla["Área de Bosques"].round(4)

    st.dataframe(tabla, width="stretch", hide_index=True)
