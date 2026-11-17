import json

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Huella ecológica en el Perú",
    page_icon="🌱",
    layout="wide"
)

st.title("Huella ecológica en el Perú")
st.caption("Huella ecológica per cápita departamental y por componentes · 2009-2016 · Fuente: MINAM (DGCIA)")

st.markdown("""
<style>
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 1180px !important;
    padding: 2.2rem 2.5rem 3rem 2.5rem !important;
    margin: 0 auto !important;
}
button[data-baseweb="tab"] { padding-left: 1rem; padding-right: 1rem; }
button[data-baseweb="tab"] p { font-size: 1.05rem; font-weight: 600; }
[data-testid="stHeaderActionElements"] { display: none; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cargar_datos():
    df = pd.read_excel("datos_set/DAG_HuellaEcologica.xlsx", header=6)
    df.columns = df.columns.str.strip()
    return df


@st.cache_data
def cargar_geojson():
    with open("datos_set/peru_departamental.geojson", encoding="utf-8") as archivo:
        return json.load(archivo)


df = cargar_datos()
geojson_peru = cargar_geojson()

def nombre_del_clic(punto):
    """Devuelve el nombre del departamento sobre el que se hizo clic en el mapa."""
    datos = punto.get("customdata")
    if datos:
        return datos[0] if isinstance(datos, (list, tuple)) else datos
    return punto.get("location")


def al_hacer_clic():
    """Se ejecuta al hacer clic en el mapa: el departamento clicado pasa a ser el
    segundo (naranja) y el que era segundo pasa a ser el primero (azul)."""
    evento = st.session_state.get("mapa_click")
    if not evento:
        return
    puntos = evento["selection"]["points"]
    if not puntos:
        return
    nombre = nombre_del_clic(puntos[-1])
    a = st.session_state.get("dpto_a")
    b = st.session_state.get("dpto_b")
    if nombre is None or a is None or b is None or nombre in (a, b):
        return
    st.session_state["dpto_a"] = b
    st.session_state["dpto_b"] = nombre

# Lista de sectores ecológicos
sectores = [
    "Huella Regional Per Capita",
    "Área de Cultivos",
    "Área de Pastoreo",
    "Área de Bosques",
    "Zonas de Pesca",
    "Huella de Carbono",
    "Áreas Urbanas"
]

TOTAL = "Huella Regional Per Capita"

# Paleta común para los gráficos
PALETA = ["#16866B", "#E08E0B", "#3B6FB6", "#B5483A", "#7A5CA8", "#5B6770"]


def tarjeta(columna, etiqueta, valor, detalle):
    """Tarjeta de cifra clave: etiqueta, valor grande y una línea de detalle.
    Las cuatro tarjetas tienen la misma estructura, así quedan del mismo alto."""
    with columna.container(border=True):
        st.caption(etiqueta)
        st.markdown(
            f"<div style='font-size:2.2rem; font-weight:700; line-height:1.15'>{valor}</div>",
            unsafe_allow_html=True
        )
        st.caption(detalle)


def lectura(texto):
    """Cuadro neutro con la interpretación escrita bajo un gráfico."""
    with st.container(border=True):
        st.markdown("**Lectura del gráfico**")
        st.write(texto)


departamentos = sorted(df["Ámbito"].unique().tolist())
anios = sorted(df["Año"].unique().tolist())


tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Inicio",
    "Evolución",
    "Ranking",
    "Comparar departamentos",
    "Acerca de"
])


with tab0:
    st.subheader("¿Qué es la huella ecológica?")
    st.write(
        "La huella ecológica per cápita estima cuánta superficie productiva necesita, "
        "en promedio, una persona de cada departamento para sostener su consumo. "
        "Se mide en hectáreas globales por persona (según la metodología de MINAM) y es "
        "la suma de seis componentes: cultivos, pastoreo, bosques, pesca, carbono y "
        "áreas urbanas. Un valor más alto significa que cada habitante demanda más "
        "recursos. Aquí se compara la huella de los 24 departamentos del Perú entre "
        "2009 y 2016."
    )

    primero, ultimo = min(anios), max(anios)
    promedio = df.groupby("Año")[TOTAL].mean()
    ranking_ini = df[df["Año"] == ultimo].sort_values(TOTAL)
    menor_ini, mayor_ini = ranking_ini.iloc[0], ranking_ini.iloc[-1]
    nombre_mayor_ini, nombre_menor_ini = mayor_ini["Ámbito"], menor_ini["Ámbito"]
    variacion = (promedio[ultimo] / promedio[primero] - 1) * 100

    # Cuatro cifras clave en tarjetas del mismo tamaño
    m1, m2, m3, m4 = st.columns(4)
    tarjeta(m1, f"Promedio {primero}", f"{promedio[primero]:.2f}", "Año base")
    tarjeta(m2, f"Promedio {ultimo}", f"{promedio[ultimo]:.2f}", f":red[{variacion:+.1f}% frente a {primero}]")
    tarjeta(m3, f"Mayor huella en {ultimo}", f"{mayor_ini[TOTAL]:.2f}", nombre_mayor_ini)
    tarjeta(m4, f"Menor huella en {ultimo}", f"{menor_ini[TOTAL]:.2f}", nombre_menor_ini)

    # Mapa de la huella total (izquierda) y tendencia del promedio (derecha)
    col_mapa, col_linea = st.columns([3, 2])

    with col_mapa:
        st.markdown("##### Huella total por departamento")
        anio_mapa = st.select_slider("Año:", options=anios, value=ultimo, key="anio_inicio")
        df_mapa = df[df["Año"] == anio_mapa]
        fig_inicio = px.choropleth(
            df_mapa,
            geojson=geojson_peru,
            locations="Ámbito",
            featureidkey="properties.NOMBDEP",
            color=TOTAL,
            color_continuous_scale="Greens",
            range_color=(df[TOTAL].min(), df[TOTAL].max()),  # misma escala en todos los años
            hover_name="Ámbito",
            hover_data={TOTAL: ":.2f", "Ámbito": False},
            labels={TOTAL: "Huella per cápita"}
        )
        fig_inicio.update_geos(
            visible=False,
            lonaxis_range=[-81.5, -68.5],
            lataxis_range=[-18.6, 0.2],
            bgcolor="rgba(0,0,0,0)"
        )
        fig_inicio.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=520,
            coloraxis_colorbar={"title": "", "thickness": 12}
        )
        st.plotly_chart(fig_inicio)

    with col_linea:
        st.markdown("##### Promedio de los departamentos por año")
        fig_prom = px.line(
            promedio.reset_index(),
            x="Año",
            y=TOTAL,
            markers=True,
            color_discrete_sequence=[PALETA[0]],
            labels={TOTAL: "Huella per cápita"}
        )
        fig_prom.update_xaxes(dtick=1)
        fig_prom.update_yaxes(rangemode="tozero")
        fig_prom.update_layout(template="plotly_white", height=520, margin={"r": 10, "t": 10, "l": 0, "b": 0})
        st.plotly_chart(fig_prom)

    lectura(
        f"El promedio de los departamentos pasó de {promedio[primero]:.2f} a {promedio[ultimo]:.2f} "
        f"entre {primero} y {ultimo} ({variacion:+.1f}%). En {ultimo}, {nombre_mayor_ini} tiene "
        f"{mayor_ini[TOTAL] / menor_ini[TOTAL]:.1f} veces la huella de {nombre_menor_ini}."
    )


with tab1:
    st.subheader("Evolución temporal por departamento")
    st.caption("Permite evaluar la tendencia de un sector ecológico específico a lo largo de los años.")

    col1, col2 = st.columns(2)
    with col1:
        sector_t1 = st.selectbox("Selecciona el Sector:", sectores, key="sec_t1")
    with col2:
        dptos_t1 = st.multiselect(
            "Selecciona Departamento(s):",
            departamentos,
            default=[d for d in ("LIMA", "AREQUIPA", "CUSCO") if d in departamentos],
            key="dpto_t1"
        )

    if dptos_t1:
        df_filtered_t1 = df[df["Ámbito"].isin(dptos_t1)].sort_values("Año")
        fig1 = px.line(
            df_filtered_t1,
            x="Año",
            y=sector_t1,
            color="Ámbito",
            markers=True,
            color_discrete_sequence=PALETA,
            title=f"Evolución de {sector_t1} ({min(anios)} - {max(anios)})",
            labels={sector_t1: "Huella per cápita", "Ámbito": "Departamento"}
        )
        fig1.update_xaxes(dtick=1)  # un número por cada año
        fig1.update_layout(template="plotly_white")
        st.plotly_chart(fig1)

        # Interpretación automática: cambio porcentual entre el primer y el último año
        cambios = {}
        for d in dptos_t1:
            serie = df_filtered_t1[df_filtered_t1["Ámbito"] == d].set_index("Año")[sector_t1]
            if serie.loc[min(anios)] > 0:
                cambios[d] = (serie.loc[max(anios)] / serie.loc[min(anios)] - 1) * 100
        if len(cambios) == 1:
            d, c = next(iter(cambios.items()))
            verbo = "aumentó" if c > 0 else "disminuyó"
            lectura(f"En {d}, {sector_t1} {verbo} {abs(c):.1f}% entre {min(anios)} y {max(anios)}.")
        elif len(cambios) > 1:
            sube = max(cambios, key=cambios.get)
            baja = min(cambios, key=cambios.get)
            lectura(
                f"Entre {min(anios)} y {max(anios)}, el mayor cambio en {sector_t1} fue en "
                f"{sube} ({cambios[sube]:+.1f}%) y el menor en {baja} ({cambios[baja]:+.1f}%)."
            )
    else:
        st.warning("Por favor, selecciona al menos un departamento para visualizar la tendencia.")


with tab2:
    st.subheader("Ranking departamental por sector")
    st.caption("Compara la magnitud de un sector ecológico específico entre todos los departamentos para un año dado.")

    col1, col2 = st.columns(2)
    with col1:
        anio_t2 = st.select_slider("Selecciona el Año:", options=anios, value=max(anios), key="anio_t2")
    with col2:
        sector_t2 = st.selectbox("Selecciona el Sector:", sectores, key="sec_t2")

    df_filtered_t2 = df[df["Año"] == anio_t2].sort_values(by=sector_t2, ascending=False)

    fig2 = px.bar(
        df_filtered_t2,
        x="Ámbito",
        y=sector_t2,
        color=sector_t2,
        color_continuous_scale="Greens",
        title=f"Comparativa de {sector_t2} en el año {anio_t2}",
        labels={"Ámbito": "Departamento", sector_t2: "Huella per cápita"}
    )
    fig2.update_layout(template="plotly_white", xaxis_tickangle=-45)
    st.plotly_chart(fig2)

    # Interpretación automática: el departamento más alto frente al más bajo
    mayor_r = df_filtered_t2.iloc[0]
    menor_r = df_filtered_t2.iloc[-1]
    nombre_mayor, nombre_menor = mayor_r["Ámbito"], menor_r["Ámbito"]
    texto_r = (
        f"En {anio_t2}, {nombre_mayor} tiene el mayor valor de {sector_t2} ({mayor_r[sector_t2]:.2f}) "
        f"y {nombre_menor} el menor ({menor_r[sector_t2]:.2f})"
    )
    if menor_r[sector_t2] > 0:
        texto_r += f": el primero es {mayor_r[sector_t2] / menor_r[sector_t2]:.1f} veces el segundo."
    else:
        texto_r += "."
    lectura(texto_r)


with tab3:
    st.subheader("Comparativa de dos departamentos")
    st.caption("Haz clic en un departamento del mapa (o usa las listas): los dos últimos elegidos se resaltan y se comparan.")

    # Controles de selección
    c1, c2, c3 = st.columns(3)
    with c1:
        anio_t3 = st.selectbox("Selecciona el Año:", anios, index=len(anios) - 1, key="anio_t3")
    with c2:
        dpto_a = st.selectbox(
            "Primer Departamento (Azul):",
            departamentos,
            index=departamentos.index("LIMA"),
            key="dpto_a"
        )
    with c3:
        
        opciones_b = [d for d in departamentos if d != dpto_a]
        dpto_b = st.selectbox("Segundo Departamento (Naranja):", opciones_b, index=0, key="dpto_b")

    st.markdown("---")

    
    col_map, col_chart = st.columns([2, 3])

    
    with col_map:
        st.markdown("##### Mapa del Perú")
        df_year = df[df["Año"] == anio_t3].copy()

        
        etiqueta_a = f"1. {dpto_a}"
        etiqueta_b = f"2. {dpto_b}"
        otros = "Otros departamentos"

        def asignar_estado(dpto):
            if dpto == dpto_a:
                return etiqueta_a
            if dpto == dpto_b:
                return etiqueta_b
            return otros

        df_year["Estado"] = df_year["Ámbito"].apply(asignar_estado)

        fig_map = px.choropleth(
            df_year,
            geojson=geojson_peru,
            locations="Ámbito",                       
            featureidkey="properties.NOMBDEP",       
            color="Estado",
            color_discrete_map={
                etiqueta_a: "#1f77b4",
                etiqueta_b: "#ff7f0e",
                otros: "rgba(140, 140, 140, 0.35)"   
            },
            category_orders={"Estado": [etiqueta_a, etiqueta_b, otros]},
            hover_name="Ámbito",
            custom_data=["Ámbito"],                  
            hover_data={"Huella Regional Per Capita": ":.2f", "Estado": False, "Ámbito": False}
        )

        
        fig_map.update_geos(
            visible=False,
            lonaxis_range=[-81.5, -68.5],
            lataxis_range=[-18.6, 0.2],
            bgcolor="rgba(0,0,0,0)"
        )
        fig_map.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.35)",
            marker_line_width=0.6,
            
            selected={"marker": {"opacity": 1}},
            unselected={"marker": {"opacity": 1}}
        )
        
        fig_map.for_each_trace(lambda t: t.update(showlegend=False) if t.name == otros else None)
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=680,
            
            legend={"title_text": "", "x": 0, "y": 0.02, "xanchor": "left", "yanchor": "bottom",
                    "bgcolor": "rgba(0,0,0,0)"}
        )
        st.plotly_chart(
            fig_map,
            on_select=al_hacer_clic,
            selection_mode="points",
            key="mapa_click",
            config={"displayModeBar": False}  
        )

    
    with col_chart:
        st.markdown(f"##### Perfil ecológico completo ({anio_t3})")
        df_t3 = df[(df["Año"] == anio_t3) & (df["Ámbito"].isin([dpto_a, dpto_b]))]

        sectores_comp = [s for s in sectores if s != "Huella Regional Per Capita"]
        df_melted = pd.melt(
            df_t3,
            id_vars=["Ámbito", "Año"],
            value_vars=sectores_comp,
            var_name="Sector",
            value_name="Huella"
        )

        fig_bar = px.bar(
            df_melted,
            x="Sector",
            y="Huella",
            color="Ámbito",
            barmode="group",
            color_discrete_map={
                dpto_a: "#1f77b4",
                dpto_b: "#ff7f0e"
            },
            title=f"Componentes: {dpto_a} vs {dpto_b}",
            labels={"Huella": "Huella per cápita", "Sector": "Componente"}
        )
        fig_bar.update_layout(
            template="plotly_white",
            xaxis_tickangle=-35,
            height=680,
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )
        st.plotly_chart(fig_bar)

    
    fila_a = df[(df["Año"] == anio_t3) & (df["Ámbito"] == dpto_a)].iloc[0]
    fila_b = df[(df["Año"] == anio_t3) & (df["Ámbito"] == dpto_b)].iloc[0]
    brechas = {s: abs(fila_a[s] - fila_b[s]) for s in sectores_comp}
    mayor_brecha = max(brechas, key=brechas.get)
    if fila_a[TOTAL] >= fila_b[TOTAL]:
        alto, bajo, v_alto, v_bajo = dpto_a, dpto_b, fila_a[TOTAL], fila_b[TOTAL]
    else:
        alto, bajo, v_alto, v_bajo = dpto_b, dpto_a, fila_b[TOTAL], fila_a[TOTAL]
    lectura(
        f"En {anio_t3}, {alto} tiene la mayor huella total ({v_alto:.2f} frente a {v_bajo:.2f} de {bajo}). "
        f"La mayor diferencia entre ambos está en {mayor_brecha}."
    )


with tab4:
    st.subheader("Acerca del proyecto")
    st.markdown("""
    ### 🌎 Sobre el proyecto

    El proyecto **Huella Ecológica del Perú (2009–2016)** consiste en el desarrollo de una plataforma web interactiva que permite explorar y analizar información relacionada con la huella ecológica per cápita de los departamentos del Perú. Mediante la representación gráfica de datos ambientales, se busca facilitar la comprensión de la demanda de recursos naturales y reconocer las diferencias existentes entre los territorios durante el periodo estudiado.

    ### 🌱 ¿Por qué es importante estudiarla?

    La huella ecológica permite comprender la presión que generan las actividades humanas sobre los recursos naturales y los ecosistemas. Su análisis resulta importante para reconocer cómo se relaciona el consumo de recursos con la capacidad de la naturaleza para regenerarlos. En el caso peruano, conocer estas variaciones permite acercarnos a la realidad ambiental de sus diferentes departamentos.

    ### 🎯 Objetivo del proyecto

    Desarrollar una herramienta digital que facilite la visualización, comparación e interpretación de la huella ecológica per cápita en los departamentos del Perú entre 2009 y 2016, utilizando gráficos interactivos y representaciones geográficas.

    ### 📊 Información analizada

    El estudio considera seis componentes de la huella ecológica: área de cultivos, área de pastoreo, área de bosques, zonas de pesca, huella de carbono y áreas urbanas. Estos componentes permiten observar diferentes aspectos de la demanda de recursos naturales y conforman la huella regional per cápita.

    ### 📁 Fuente de información

    La información utilizada procede de la documentación del Ministerio del Ambiente (MINAM), a través de la Dirección General de Información e Investigación Ambiental (DGCIA). La base de datos comprende el periodo 2009–2016 y considera 24 ámbitos departamentales. Los valores se expresan en hectáreas globales por persona.

    ### 💻 Desarrollo de la plataforma

    Para el desarrollo se utilizaron herramientas de programación y visualización de datos como Python, Pandas, Plotly y Streamlit. Estas permitieron organizar la información, elaborar gráficos interactivos, representar los datos en un mapa del Perú y facilitar la comparación entre departamentos y años.

    ### 🌿 Aporte del proyecto

    Esta plataforma busca acercar la información ambiental a los usuarios de una manera visual y comprensible. Asimismo, permite reconocer diferencias y variaciones en los indicadores analizados, promoviendo el interés por el estudio de la huella ecológica y la importancia del uso responsable de los recursos naturales.

    ---

    **Integrantes:** Rose Angel Suazo Davila y Maria Fernanda Perez Salvatierra.

    **Fuente:** Ministerio del Ambiente (MINAM) – DGCIA.""")

