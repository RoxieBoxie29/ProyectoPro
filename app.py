import streamlit as st
import pandas as pd

st.title("Área de pastoreo por departamento")

df = pd.read_excel("datos_set/DAG_HuellaEcologica.xlsx", header=6)

deptos = st.multiselect(
    "Departamentos",
    sorted(df["Ámbito"].unique()),
    default=["LIMA", "AREQUIPA", "CUSCO"],
)

if deptos:
    tabla = df[df["Ámbito"].isin(deptos)].pivot_table(
        index="Año", columns="Ámbito", values="Área de Pastoreo"
    )
    tabla.index = tabla.index.astype(str)
    st.line_chart(tabla)
else:
    st.info("Elige al menos un departamento.")
