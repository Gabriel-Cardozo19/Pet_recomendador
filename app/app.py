import os
import pandas as pd
import streamlit as st

# -----------------------------------
# Configuración general
# -----------------------------------
st.set_page_config(
    page_title="Webshop | Cross-Selling",
    page_icon="🛒",
    layout="wide"
)

# -----------------------------------
# Estilos
# -----------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #2563EB;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.4rem;
    }
    .section-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        min-height: 190px;
    }
    .card h4 {
        margin: 0 0 10px 0;
        color: #0F172A;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .card p {
        margin: 6px 0;
        color: #334155;
        font-size: 0.98rem;
    }
    .insight-box {
        background-color: #ECFDF5;
        border-left: 6px solid #10B981;
        padding: 16px;
        border-radius: 12px;
        color: #065F46;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 6px solid #2563EB;
        padding: 16px;
        border-radius: 12px;
        color: #1E3A8A;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .warn-box {
        background-color: #FEFCE8;
        border-left: 6px solid #CA8A04;
        padding: 16px;
        border-radius: 12px;
        color: #854D0E;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .action-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 16px;
        min-height: 170px;
    }
    .action-card h4 {
        color: #334155;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    .action-card p {
        color: #64748B;
        font-size: 0.98rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Carga de datos
# -----------------------------------
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "processed", "recomendaciones_modelo.csv")

    if not os.path.exists(path):
        st.error(f"No se encontró el archivo: {path}")
        st.stop()

    return pd.read_csv(path)

recomendaciones = load_data()

# -----------------------------------
# Columnas del dataset
# -----------------------------------
col_origen = "grupo_a"
col_reco = "grupo_b"
col_score = "score"
col_freq = "frecuencia"
col_ticket = "ticket_grupo_b"

# -----------------------------------
# Funciones auxiliares
# -----------------------------------
def clasificar_oportunidad(score: float) -> str:
    if score >= 0.13:
        return "Alta"
    elif score >= 0.08:
        return "Media"
    return "Baja"

def clasificar_potencial(ticket: float) -> str:
    if ticket >= 130:
        return "Alto potencial comercial"
    elif ticket >= 110:
        return "Potencial comercial moderado"
    return "Potencial comercial acotado"

def descripcion_categoria(grupo: str) -> str:
    descripciones = {
        "Alimentos": "Productos de consumo frecuente y alta recurrencia.",
        "Cuidado Personal": "Productos de higiene, bienestar y cuidado diario.",
        "Recreación": "Consumo vinculado a ocio, entretenimiento y bienestar.",
        "Automotor": "Compras más específicas, con tickets unitarios relevantes.",
        "Hogar": "Artículos funcionales y de uso cotidiano.",
        "Tecnología": "Productos de valor percibido mayor y potencial de ticket superior.",
        "Moda": "Consumo asociado a preferencia, estilo y estacionalidad.",
        "Industria y construcción": "Productos específicos asociados a necesidades puntuales.",
        "Marketplace": "Categoría amplia y heterogénea dentro del catálogo.",
        "Cultura y entretenimiento": "Consumo asociado a experiencias y ocio."
    }
    return descripciones.get(grupo, "Categoría con comportamiento específico dentro del catálogo.")

# -----------------------------------
# Logo + Header
# -----------------------------------
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

col_logo, col_title = st.columns([1, 7])

with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=95)

with col_title:
    st.markdown(
        '<div class="main-title">Oportunidades de Cross-Selling</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Identificación de oportunidades comerciales entre categorías para aumentar ventas y ticket promedio.</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.header("Configuración del análisis")

grupos = sorted(recomendaciones[col_origen].dropna().unique())
grupo_seleccionado = st.sidebar.selectbox("Seleccionar categoría analizada", grupos)
top_k = st.sidebar.slider("Cantidad de oportunidades a visualizar", 3, 10, 5)

# -----------------------------------
# Filtrado
# -----------------------------------
df_grupo = (
    recomendaciones[recomendaciones[col_origen] == grupo_seleccionado]
    .sort_values(col_score, ascending=False)
    .head(top_k)
    .copy()
)

# -----------------------------------
# Variables principales
# -----------------------------------
if not df_grupo.empty:
    mejor = df_grupo.iloc[0][col_reco]
    mejor_score = float(df_grupo.iloc[0][col_score])
    mejor_freq = int(df_grupo.iloc[0][col_freq])
    mejor_ticket = float(df_grupo.iloc[0][col_ticket])

    nivel_oportunidad = clasificar_oportunidad(mejor_score)
    potencial = clasificar_potencial(mejor_ticket)
    score_promedio = float(df_grupo[col_score].mean())
else:
    mejor = "-"
    mejor_score = 0.0
    mejor_freq = 0
    mejor_ticket = 0.0
    nivel_oportunidad = "-"
    potencial = "-"
    score_promedio = 0.0

# -----------------------------------
# Resumen ejecutivo
# -----------------------------------
st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Categoría analizada", grupo_seleccionado)

with col2:
    st.metric("Mayor oportunidad detectada", mejor)

with col3:
    st.metric("Nivel de oportunidad", nivel_oportunidad)

st.markdown("---")

# -----------------------------------
# Insight principal
# -----------------------------------
st.markdown("### Relación comercial detectada")
st.markdown(
    f"""
    <div class="info-box">
    La categoría <b>{grupo_seleccionado}</b> concentra clientes con afinidad hacia <b>{mejor}</b>, 
    lo que sugiere una oportunidad concreta para activar estrategias de venta cruzada.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="card">
        <h4>Oportunidad principal sugerida</h4>
        <p>Para la categoría <b>{grupo_seleccionado}</b>, la principal oportunidad detectada es <b>{mejor}</b>.</p>
        <p><b>Nivel de oportunidad:</b> {nivel_oportunidad}</p>
        <p><b>Compras conjuntas observadas:</b> {mejor_freq}</p>
        <p><b>Impacto económico estimado:</b> ${mejor_ticket:,.2f}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="warn-box">
    <b>{potencial}</b>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Oportunidades principales
# -----------------------------------
st.markdown('<div class="section-title">Principales oportunidades sugeridas</div>', unsafe_allow_html=True)

if df_grupo.empty:
    st.warning("No se encontraron oportunidades para esta categoría.")
else:
    card_cols = st.columns(min(3, len(df_grupo)))

    for idx, (_, row) in enumerate(df_grupo.head(3).iterrows()):
        with card_cols[idx]:
            st.markdown(
                f"""
                <div class="card">
                    <h4>{row[col_reco]}</h4>
                    <p><b>Nivel de oportunidad:</b> {clasificar_oportunidad(float(row[col_score]))}</p>
                    <p><b>Compras conjuntas:</b> {int(row[col_freq])}</p>
                    <p><b>Ticket promedio:</b> ${float(row[col_ticket]):,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# -----------------------------------
# Detalle + Aplicación comercial
# -----------------------------------
left, right = st.columns([1.35, 1])

with left:
    st.markdown('<div class="section-title">Detalle</div>', unsafe_allow_html=True)
    st.caption("Vista detallada para análisis y validación de las oportunidades detectadas.")

    if not df_grupo.empty:
        tabla = df_grupo[[col_reco, col_score, col_freq, col_ticket]].rename(columns={
            col_reco: "Categoría sugerida",
            col_score: "Nivel de oportunidad",
            col_freq: "Compras conjuntas",
            col_ticket: "Impacto económico ($)"
        })

        tabla["Impacto económico ($)"] = tabla["Impacto económico ($)"].apply(lambda x: f"${x:,.2f}")
        tabla["Nivel de oportunidad"] = tabla["Nivel de oportunidad"].apply(lambda x: f"{x:.4f}")

        with st.expander("Ver detalle completo"):
            st.dataframe(tabla, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Aplicación comercial</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            """
            <div class="action-card">
                <h4>🛒 Bundle recomendado</h4>
                <p>Probar combinaciones comerciales entre categorías relacionadas para aumentar valor por compra.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_b:
        st.markdown(
            """
            <div class="action-card">
                <h4>🎯 Sugerencia en carrito</h4>
                <p>Usar recomendaciones cruzadas durante la navegación o el checkout para impulsar conversión.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_c:
        st.markdown(
            """
            <div class="action-card">
                <h4>📢 Campaña segmentada</h4>
                <p>Activar promociones dirigidas según afinidad detectada entre categorías.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------
# Explicación de negocio
# -----------------------------------
st.markdown("### ¿Por qué esta relación importa?")
st.write(
    f"""
Los clientes que compran en **{grupo_seleccionado}** también tienden a comprar en **{mejor}**, 
lo que representa una oportunidad directa para aumentar el ticket promedio mediante estrategias de cross-selling.

Esta recomendación se apoya en una recurrencia observada de **{mejor_freq} compras conjuntas** y en un 
impacto económico estimado de **${mejor_ticket:,.2f}** para la categoría sugerida.
"""
)

if score_promedio >= 0.13:
    st.success("La oportunidad detectada muestra una afinidad comercial alta dentro del catálogo.")
elif score_promedio >= 0.08:
    st.info("La oportunidad detectada presenta una afinidad comercial moderada y puede activarse con foco táctico.")
else:
    st.warning("La oportunidad detectada es más limitada y conviene validarla antes de una activación amplia.")

st.markdown("### Nivel de oportunidad")
st.progress(min(mejor_score / 0.20, 1.0))

st.markdown("---")

# -----------------------------------
# Aporte y próximos pasos
# -----------------------------------
colA, colB = st.columns(2)

with colA:
    st.markdown("## ¿Qué aporta esta herramienta?")
    st.markdown("""
Permite transformar datos históricos en oportunidades concretas de cross-selling, ayudando a:

- identificar combinaciones con mayor potencial comercial
- priorizar acciones para aumentar el ticket promedio
- sostener decisiones de recomendación con evidencia del comportamiento de compra
""")

with colB:
    st.markdown("## Próximos pasos")
    st.markdown("""
Como evolución del proyecto, el sistema puede avanzar hacia:

- recomendaciones más granulares
- mayor nivel de personalización
- integración con otras capas de activación comercial
""")

st.markdown("---")
st.caption("Proyecto Webshop · Sprint 2")