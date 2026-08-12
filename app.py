# ============================================================
# VWFS - APPLICATION D'AIDE À LA DÉCISION
# ============================================================

import os
import base64
import sqlite3
import joblib
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CHEMINS ROBUSTES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def chemin_fichier(nom):
    return os.path.join(BASE_DIR, nom)

def logo_base64():
    """Retourne le logo local en base64 pour l'intégrer proprement dans le HTML."""
    chemin = chemin_fichier("logo_vwfs.png")
    if not os.path.exists(chemin):
        return ""
    with open(chemin, "rb") as fichier:
        return base64.b64encode(fichier.read()).decode("utf-8")



# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VWFS | Pilotage & Prévisions",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SYSTÈME VISUEL — TOKENS
# ============================================================
# Palette dérivée du bleu institutionnel VWFS, resserrée autour
# de quelques teintes nommées pour garder une identité cohérente
# sur toute l'application (cartes, graphiques, badges).
#
#   --navy-950   #071022   fond profond / dégradés sidebar
#   --navy-900   #0A1F44   navy principal (texte fort, hero)
#   --navy-700   #14315E   navy secondaire
#   --blue-600   #0072CE   accent VW (CTA, liens, séries data)
#   --blue-300   #6FB6FF   accent clair (highlights, hover)
#   --ink-900    #101B2D   texte principal
#   --ink-500    #5B6B84   texte secondaire
#   --line-200   #E4E9F2   bordures, séparateurs
#   --surface    #FFFFFF   fond des cartes
#   --canvas     #F5F7FB   fond de page
#   --good-600   #17924F   succès / objectif atteint
#   --warn-600   #C97A17   vigilance
#   --bad-600    #D1493B   alerte

PALETTE_CATEGORIES = [
    "#0072CE", "#0A1F44", "#6FB6FF",
    "#17924F", "#C97A17", "#7C5CC4"
]

PALETTE_SEQUENTIELLE = [
    "#EAF3FF", "#C7E1FF", "#8FC2FF",
    "#4FA0F5", "#0072CE", "#0A1F44"
]


# ============================================================
# CHARTE VISUELLE
# ============================================================

st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root{
    --vw-navy:#001E50;
    --vw-navy-2:#0A315F;
    --vw-blue:#0066CC;
    --vw-cyan:#00A6D6;
    --canvas:#F4F7FB;
    --surface:#FFFFFF;
    --surface-2:#F8FAFD;
    --text:#142033;
    --muted:#66758C;
    --line:#E3E9F1;
    --good:#168657;
    --warn:#C47A1A;
    --bad:#D14B43;
    --shadow:0 12px 34px rgba(0,30,80,.08);
}

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
    color:var(--text);
}

/* Page */
.stApp{
    background:
      radial-gradient(circle at 88% -10%, rgba(0,102,204,.10), transparent 28%),
      linear-gradient(180deg,#F8FAFD 0%,var(--canvas) 100%);
}
.block-container{
    max-width:1480px;
    padding-top:1.15rem;
    padding-bottom:3.5rem;
}

/* Hide Streamlit chrome where possible */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{
    background:rgba(255,255,255,.92);
    backdrop-filter:blur(10px);
    border-bottom:1px solid rgba(227,233,241,.9);
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:
      linear-gradient(180deg,#071A38 0%,#0B2A55 52%,#123B71 100%);
    border-right:1px solid rgba(255,255,255,.06);
}
section[data-testid="stSidebar"] > div{
    padding-top:1rem;
}
section[data-testid="stSidebar"] *{
    font-family:'Inter',sans-serif;
}
section[data-testid="stSidebar"] label{
    color:#D9E5F4 !important;
    font-weight:600 !important;
    font-size:.82rem !important;
}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small{
    color:#94AAC7 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div{
    background:#FFFFFF !important;
    border:1px solid rgba(255,255,255,.22) !important;
    border-radius:12px !important;
    min-height:44px;
    box-shadow:none !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] span{
    color:#20324A !important;
}
section[data-testid="stSidebar"] hr{
    border-color:rgba(255,255,255,.14);
}
.sidebar-shell{
    padding:.15rem .15rem .3rem;
}
.sidebar-brand{
    display:flex;
    align-items:center;
    gap:11px;
    margin:0 0 18px 0;
}
.sidebar-logo-card{
    width:66px;
    height:66px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#FFFFFF;
    border-radius:16px;
    box-shadow:0 10px 28px rgba(0,0,0,.15);
    overflow:hidden;
}
.sidebar-logo-card img{
    width:58px;
    height:auto;
    object-fit:contain;
}
.sidebar-brand-copy{
    line-height:1.15;
}
.sidebar-brand-title{
    color:white;
    font-family:'Manrope',sans-serif;
    font-weight:800;
    font-size:1.02rem;
}
.sidebar-brand-sub{
    color:#79BFFF;
    font-size:.67rem;
    letter-spacing:1.4px;
    font-weight:700;
    text-transform:uppercase;
    margin-top:5px;
}
.sidebar-section-title{
    color:#FFFFFF;
    font-family:'Manrope',sans-serif;
    font-size:1rem;
    font-weight:800;
    margin:10px 0 2px;
}
.sidebar-section-sub{
    color:#9FB3CF;
    font-size:.77rem;
    margin-bottom:15px;
}
.sidebar-foot{
    color:#9FB3CF;
    font-size:.72rem;
    line-height:1.55;
    padding:4px 1px 0;
}

/* Hero */
.exec-hero{
    position:relative;
    overflow:hidden;
    border-radius:24px;
    padding:34px 38px;
    color:white;
    background:
      radial-gradient(circle at 88% 16%,rgba(42,156,255,.36),transparent 24%),
      linear-gradient(120deg,#061B3D 0%,#002E68 48%,#0066CC 120%);
    box-shadow:0 22px 48px rgba(0,30,80,.19);
    margin:2px 0 22px;
}
.exec-hero:before{
    content:"";
    position:absolute;
    inset:0;
    background-image:radial-gradient(rgba(255,255,255,.18) 1px,transparent 1px);
    background-size:24px 24px;
    opacity:.18;
    mask-image:linear-gradient(105deg,#000,transparent 70%);
}
.exec-hero-inner{
    position:relative;
    z-index:2;
    display:flex;
    justify-content:space-between;
    gap:30px;
    align-items:center;
}
.exec-hero-copy{max-width:850px;}
.exec-eyebrow{
    color:#99CBFF;
    font-size:.70rem;
    font-weight:800;
    letter-spacing:2.1px;
    text-transform:uppercase;
    margin-bottom:10px;
}
.exec-title{
    font-family:'Manrope',sans-serif;
    font-weight:800;
    font-size:2.18rem;
    line-height:1.12;
    letter-spacing:-.5px;
    margin:0 0 10px;
    color:#FFFFFF;
}
.exec-subtitle{
    color:#D8E7F7;
    font-size:.98rem;
    line-height:1.65;
    max-width:760px;
}
.exec-chip-row{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:18px;
}
.exec-chip{
    display:inline-flex;
    align-items:center;
    padding:7px 11px;
    border-radius:999px;
    font-size:.70rem;
    color:#EAF4FF;
    font-weight:700;
    background:rgba(255,255,255,.10);
    border:1px solid rgba(255,255,255,.16);
}
.exec-logo{
    flex:0 0 auto;
    width:128px;
    height:128px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#FFFFFF;
    border-radius:23px;
    padding:14px;
    box-shadow:0 14px 34px rgba(0,0,0,.18);
}
.exec-logo img{
    width:100%;
    height:100%;
    object-fit:contain;
}

/* Tabs */
div[data-baseweb="tab-list"]{
    gap:4px;
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:14px;
    padding:5px;
    box-shadow:0 4px 16px rgba(0,30,80,.04);
    margin-bottom:16px;
}
button[data-baseweb="tab"]{
    border-radius:10px !important;
    font-weight:650 !important;
    color:var(--muted) !important;
    min-height:42px;
}
button[data-baseweb="tab"][aria-selected="true"]{
    color:var(--vw-navy) !important;
    background:#EDF5FF !important;
}
div[data-baseweb="tab-highlight"]{
    display:none !important;
}

/* Section headings */
h1,h2,h3{
    font-family:'Manrope',sans-serif !important;
    color:var(--vw-navy) !important;
    letter-spacing:-.25px;
}
h2{
    font-size:1.55rem !important;
    font-weight:800 !important;
}
h3{
    font-size:1.05rem !important;
    font-weight:750 !important;
}

/* KPI cards */
.kpi-card{
    position:relative;
    min-height:122px;
    padding:19px 19px 17px 21px;
    border:1px solid var(--line);
    border-radius:18px;
    background:linear-gradient(180deg,#FFFFFF 0%,#FBFCFE 100%);
    box-shadow:0 8px 24px rgba(0,30,80,.055);
    overflow:hidden;
}
.kpi-card:before{
    content:"";
    position:absolute;
    left:0; top:0; bottom:0;
    width:4px;
    background:linear-gradient(180deg,var(--vw-blue),var(--vw-cyan));
}
.kpi-label{
    color:var(--muted);
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.5px;
    text-transform:uppercase;
    margin-bottom:9px;
}
.kpi-value{
    font-family:'Manrope',sans-serif;
    color:var(--vw-navy);
    font-size:1.62rem;
    line-height:1.1;
    font-weight:800;
}
.kpi-note{
    color:#93A1B6;
    font-size:.70rem;
    margin-top:8px;
    font-weight:500;
}

/* Generic cards */
.section-card,
.result-card{
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:18px;
    padding:20px 22px;
    box-shadow:0 8px 24px rgba(0,30,80,.05);
    line-height:1.65;
    color:var(--muted);
}
.section-card{margin-bottom:16px;}
.result-card{
    background:linear-gradient(135deg,#EDF6FF,#FFFFFF);
    border-color:#CDE3FA;
}
.model-badge{
    display:inline-flex;
    align-items:center;
    padding:6px 11px;
    border-radius:999px;
    background:#EAF3FF;
    color:var(--vw-blue);
    font-size:.68rem;
    font-weight:800;
    letter-spacing:.65px;
    text-transform:uppercase;
}
.model-card h3{
    margin:8px 0 10px !important;
}
.model-card{
    min-height:210px;
    color:var(--muted);
    line-height:1.9;
}

/* Dataframe / expander */
div[data-testid="stDataFrame"]{
    border:1px solid var(--line);
    border-radius:14px;
    overflow:hidden;
    box-shadow:0 5px 20px rgba(0,30,80,.04);
}
details{
    background:#FFFFFF !important;
    border:1px solid var(--line) !important;
    border-radius:14px !important;
}

/* Inputs / buttons */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div{
    border-radius:11px !important;
}
div.stButton > button,
div.stDownloadButton > button,
button[kind="primary"]{
    border-radius:11px !important;
    min-height:44px;
    font-weight:700 !important;
}
button[kind="primary"]{
    background:linear-gradient(120deg,#0066CC,#003D7A) !important;
    border:none !important;
    box-shadow:0 9px 22px rgba(0,102,204,.22);
}
div[data-testid="stAlert"]{
    border-radius:14px;
}

/* Small executive intro */
.exec-strip{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:18px;
    padding:13px 16px;
    margin:0 0 14px;
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:14px;
    box-shadow:0 5px 18px rgba(0,30,80,.035);
}
.exec-strip-title{
    color:var(--vw-navy);
    font-weight:800;
    font-family:'Manrope',sans-serif;
}
.exec-strip-note{
    color:var(--muted);
    font-size:.78rem;
}
.exec-status{
    white-space:nowrap;
    color:#0D6A46;
    font-size:.72rem;
    font-weight:800;
    padding:6px 10px;
    background:#E8F6EF;
    border-radius:999px;
}

/* Executive insights */
.insight-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:8px 0 18px;}
.insight-card{background:linear-gradient(180deg,#FFFFFF,#F8FBFF);border:1px solid var(--line);border-radius:16px;padding:16px 18px;box-shadow:0 7px 20px rgba(0,30,80,.045);}
.insight-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.7px;font-weight:800;color:#7A8BA3;margin-bottom:7px;}
.insight-value{font-family:'Manrope',sans-serif;font-size:1.05rem;line-height:1.35;color:var(--vw-navy);font-weight:800;}
.insight-note{font-size:.76rem;color:var(--muted);line-height:1.55;margin-top:6px;}
.compare-box{background:#FFFFFF;border:1px solid var(--line);border-radius:18px;padding:18px 20px;box-shadow:0 8px 24px rgba(0,30,80,.045);margin:6px 0 16px;}
.compare-title{font-family:'Manrope',sans-serif;color:var(--vw-navy);font-weight:800;font-size:1.02rem;margin-bottom:3px;}
.compare-sub{color:var(--muted);font-size:.77rem;}
.comment-card{background:linear-gradient(135deg,#F0F7FF,#FFFFFF);border:1px solid #CFE3F8;border-left:4px solid var(--vw-blue);border-radius:14px;padding:15px 17px;margin:10px 0 16px;color:#3F5068;line-height:1.6;font-size:.88rem;}
.comment-card b{color:var(--vw-navy);}
.rank-card{background:#FFFFFF;border:1px solid var(--line);border-radius:16px;padding:16px 18px;min-height:132px;box-shadow:0 6px 20px rgba(0,30,80,.04);}
.rank-pos{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:#EDF5FF;color:var(--vw-blue);font-weight:800;font-family:'Manrope',sans-serif;margin-bottom:8px;}
.rank-name{color:var(--vw-navy);font-weight:800;font-family:'Manrope',sans-serif;}
.rank-value{color:var(--muted);font-size:.78rem;margin-top:4px;}
@media (max-width: 900px){.insight-grid{grid-template-columns:1fr;}}


/* Final decision-support blocks */
.decision-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:10px 0 18px;}
.decision-card{background:linear-gradient(180deg,#FFFFFF,#F8FBFF);border:1px solid var(--line);border-radius:17px;padding:17px 18px;box-shadow:0 7px 22px rgba(0,30,80,.045);}
.decision-title{font-family:'Manrope',sans-serif;font-weight:800;color:var(--vw-navy);font-size:.96rem;margin-bottom:7px;}
.decision-text{color:var(--muted);font-size:.84rem;line-height:1.6;}
.decision-good{border-left:4px solid var(--good);}
.decision-warn{border-left:4px solid var(--warn);}
.decision-blue{border-left:4px solid var(--vw-blue);}
.decision-bad{border-left:4px solid var(--bad);}
@media (max-width: 900px){.decision-grid{grid-template-columns:1fr;}}

</style>
""",
unsafe_allow_html=True
)


# ============================================================
# FONCTIONS
# ============================================================

def format_euros(valeur):

    valeur = float(valeur)

    if abs(valeur) >= 1_000_000_000:
        return f"{valeur / 1_000_000_000:.2f} Md€"

    if abs(valeur) >= 1_000_000:
        return f"{valeur / 1_000_000:.2f} M€"

    if abs(valeur) >= 1_000:
        return f"{valeur / 1_000:.1f} k€"

    return f"{valeur:,.0f} €".replace(",", " ")


def format_nombre(valeur):
    return f"{float(valeur):,.0f}".replace(",", " ")


def trimestre_depuis_mois(mois):
    return f"T{((int(mois) - 1) // 3) + 1}"


def carte_kpi(titre, valeur, note=""):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{titre}</div>
            <div class="kpi-value">{valeur}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )




def commentaire_scenario_regression(prediction, objectif, ecart_pct):
    if objectif <= 0:
        return (
            "Le scénario fournit une estimation du volume financier. "
            "Aucun objectif financier n'a été défini pour calculer un écart."
        )

    if ecart_pct >= 5:
        return (
            f"Le scénario se situe au-dessus de l'objectif de <b>{abs(ecart_pct):.1f} %</b>. "
            "Le niveau simulé apparaît favorable. Les variables les plus influentes du modèle, "
            "notamment les leads et le montant financé moyen, peuvent être suivies comme leviers d'analyse."
        )
    elif ecart_pct >= 0:
        return (
            f"Le scénario dépasse légèrement l'objectif de <b>{abs(ecart_pct):.1f} %</b>. "
            "La marge reste limitée ; il est pertinent de surveiller les indicateurs commerciaux avant arbitrage."
        )
    elif ecart_pct > -10:
        return (
            f"Le scénario reste sous l'objectif de <b>{abs(ecart_pct):.1f} %</b>. "
            "L'écart est modéré. Une analyse des leads, du niveau d'activité et du montant moyen financé "
            "peut aider à identifier les leviers potentiels."
        )
    else:
        return (
            f"Le scénario se situe nettement sous l'objectif de <b>{abs(ecart_pct):.1f} %</b>. "
            "Le résultat invite à revoir les hypothèses du scénario et à analyser les principaux facteurs de performance."
        )


def commentaire_classification(probabilite):
    if probabilite >= 70:
        return (
            "Le signal est favorable. La probabilité estimée est relativement élevée, "
            "mais elle doit rester un indicateur d'aide à la décision et non une certitude."
        )
    elif probabilite >= 40:
        return (
            "Le scénario se situe dans une zone intermédiaire. "
            "Une analyse complémentaire des hypothèses commerciales est recommandée avant décision."
        )
    return (
        "Le signal est faible. Le scénario mérite une analyse des leviers commerciaux et financiers "
        "avant validation, sans interpréter cette estimation comme une décision automatique."
    )


def diagnostic_executif(region_resume, reseau_resume, objectif_pct):
    messages = []

    if not region_resume.empty:
        top = region_resume.iloc[0]
        messages.append(
            f"<b>{top['region']}</b> est la région la plus contributrice au volume financier "
            f"sur le périmètre sélectionné."
        )

    if not reseau_resume.empty:
        top_r = reseau_resume.iloc[0]
        messages.append(
            f"<b>{top_r['reseau']}</b> est le réseau le plus performant en volume financier."
        )

    if objectif_pct < 30:
        messages.append(
            f"Le taux d'objectifs atteints reste limité à <b>{objectif_pct:.1f} %</b>, "
            "ce qui constitue un point d'attention."
        )
    elif objectif_pct < 60:
        messages.append(
            f"Le taux d'objectifs atteints est de <b>{objectif_pct:.1f} %</b> : "
            "la performance est intermédiaire et mérite un suivi."
        )
    else:
        messages.append(
            f"Le taux d'objectifs atteints est élevé à <b>{objectif_pct:.1f} %</b>."
        )

    return " ".join(messages)


def variation_pct(valeur_a, valeur_b):
    if valeur_b == 0:
        return 0.0
    return ((valeur_a - valeur_b) / abs(valeur_b)) * 100


def texte_comparaison(nom_a, nom_b, vol_a, vol_b, ventes_a, ventes_b, taux_a, taux_b):
    ecart_vol = variation_pct(vol_a, vol_b)
    ecart_ventes = variation_pct(ventes_a, ventes_b)
    ecart_taux = taux_a - taux_b

    leader = nom_a if vol_a >= vol_b else nom_b
    autre = nom_b if vol_a >= vol_b else nom_a

    phrases = [
        f"<b>{leader}</b> affiche le volume financier le plus élevé, "
        f"avec un écart d'environ <b>{abs(ecart_vol):.1f} %</b> par rapport à {autre}."
    ]

    if abs(ecart_ventes) >= 5:
        sens = "supérieur" if ecart_ventes > 0 else "inférieur"
        phrases.append(
            f"Le nombre de ventes de <b>{nom_a}</b> est {sens} de "
            f"<b>{abs(ecart_ventes):.1f} %</b> à celui de {nom_b}."
        )
    else:
        phrases.append(
            f"Les volumes de ventes de {nom_a} et {nom_b} restent relativement proches."
        )

    if abs(ecart_taux) >= 1:
        meilleur_taux = nom_a if taux_a >= taux_b else nom_b
        phrases.append(
            f"<b>{meilleur_taux}</b> présente le meilleur taux de financement "
            f"(écart de {abs(ecart_taux):.1f} point)."
        )

    return " ".join(phrases)


def theme_figure(fig, hauteur=None):
    """Applique une mise en forme cohérente à toutes les figures Plotly."""

    fig.update_layout(
        font=dict(family="Inter, sans-serif", color="#5B6B84", size=12.5),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            font=dict(size=11.5),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#0A1F44",
            font_color="white",
            font_family="Inter, sans-serif",
            bordercolor="#0A1F44"
        ),
        margin=dict(l=10, r=10, t=20, b=10)
    )

    if hauteur:
        fig.update_layout(height=hauteur)

    fig.update_xaxes(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7")
    fig.update_yaxes(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7")

    return fig


# ============================================================
# DONNÉES
# ============================================================

@st.cache_data
def charger_donnees():

    connexion = sqlite3.connect(chemin_fichier("base_vwfs.db"))

    df_local = pd.read_sql_query(
        """
        SELECT *
        FROM performance_commerciale
        """,
        connexion
    )

    connexion.close()

    df_local["date_observation"] = pd.to_datetime(
        df_local["date_observation"]
    )

    return df_local


# ============================================================
# MODÈLES
# ============================================================

@st.cache_resource
def charger_modele_regression():
    return joblib.load(chemin_fichier("modele_regression_vwfs.pkl"))


@st.cache_resource
def charger_modele_classification():
    return joblib.load(chemin_fichier("modele_classification_vwfs.pkl"))


try:
    df = charger_donnees()

    modele_regression = charger_modele_regression()

    modele_classification = (
        charger_modele_classification()
    )

except Exception as erreur:

    st.error(
        "Erreur lors du chargement de l'application."
    )

    st.code(str(erreur))

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    logo64 = logo_base64()

    if logo64:
        st.markdown(
            f"""
<div class="sidebar-shell">
    <div class="sidebar-brand">
        <div class="sidebar-logo-card">
            <img src="data:image/png;base64,{logo64}" alt="VWFS">
        </div>
        <div class="sidebar-brand-copy">
            <div class="sidebar-brand-title">VWFS</div>
            <div class="sidebar-brand-sub">Decision Intelligence</div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
<div class="sidebar-brand-copy" style="margin-bottom:18px;">
    <div class="sidebar-brand-title">VWFS</div>
    <div class="sidebar-brand-sub">Decision Intelligence</div>
</div>
""",
            unsafe_allow_html=True
        )

    st.markdown(
        """
<div class="sidebar-section-title">Filtres d'analyse</div>
<div class="sidebar-section-sub">Affinez le périmètre du tableau de bord</div>
""",
        unsafe_allow_html=True
    )

    annees = ["Toutes"] + sorted(
        df["annee"].unique().tolist()
    )

    regions = ["Toutes"] + sorted(
        df["region"].unique().tolist()
    )

    reseaux = ["Tous"] + sorted(
        df["reseau"].unique().tolist()
    )

    segments = ["Tous"] + sorted(
        df["private_fleet"].unique().tolist()
    )

    annee_sel = st.selectbox(
        "Année",
        annees
    )

    region_sel = st.selectbox(
        "Région",
        regions
    )

    reseau_sel = st.selectbox(
        "Réseau",
        reseaux
    )

    segment_sel = st.selectbox(
        "Segment",
        segments
    )

    st.divider()

    st.markdown(
        """
<div class="sidebar-foot">
    <b style="color:#FFFFFF;">Prototype Data & IA</b><br>
    Données entièrement simulées<br>
    Modèles sous supervision humaine
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# FILTRAGE
# ============================================================

df_filtre = df.copy()

if annee_sel != "Toutes":
    df_filtre = df_filtre[
        df_filtre["annee"] == annee_sel
    ]

if region_sel != "Toutes":
    df_filtre = df_filtre[
        df_filtre["region"] == region_sel
    ]

if reseau_sel != "Tous":
    df_filtre = df_filtre[
        df_filtre["reseau"] == reseau_sel
    ]

if segment_sel != "Tous":
    df_filtre = df_filtre[
        df_filtre["private_fleet"]
        == segment_sel
    ]


# ============================================================
# HERO
# ============================================================

logo64 = logo_base64()

logo_html = (
    f'<div class="exec-logo"><img src="data:image/png;base64,{logo64}" alt="Volkswagen Financial Services"></div>'
    if logo64
    else '<div class="exec-logo" style="font-family:Manrope,sans-serif;color:#001E50;font-weight:800;">VWFS</div>'
)

st.markdown(
    f"""
<div class="exec-hero">
  <div class="exec-hero-inner">
    <div class="exec-hero-copy">
      <div class="exec-eyebrow">DATA • PERFORMANCE • PRÉVISION</div>
      <div class="exec-title">Cockpit de pilotage commercial & financier</div>
      <div class="exec-subtitle">
        Analysez l'activité, comparez les performances et simulez des scénarios
        prédictifs à partir d'un même espace décisionnel.
      </div>
      <div class="exec-chip-row">
        <span class="exec-chip">Dashboard exécutif</span>
        <span class="exec-chip">Random Forest</span>
        <span class="exec-chip">Logistic Regression</span>
        <span class="exec-chip">Données simulées</span>
      </div>
    </div>
    {logo_html}
  </div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Vue exécutive",
        "Prévision financière",
        "Atteinte d'objectif",
        "Modèles & gouvernance"
    ]
)


# ============================================================
# ONGLET 1 - DASHBOARD
# ============================================================

with tab1:

    st.markdown(
        """
<div class="exec-strip">
    <div>
        <div class="exec-strip-title">Vue d'ensemble de la performance</div>
        <div class="exec-strip-note">Indicateurs consolidés selon les filtres sélectionnés</div>
    </div>
    <div class="exec-status">● Données chargées</div>
</div>
""",
        unsafe_allow_html=True
    )

    volume_total = (
        df_filtre["chiffre_affaires_eur"]
        .sum()
    )

    ventes_total = (
        df_filtre["nb_ventes"]
        .sum()
    )

    contrats_total = (
        df_filtre[
            "nb_contrats_financement"
        ]
        .sum()
    )

    objectif_pct = (
        df_filtre["objectif_atteint"]
        .mean() * 100
        if len(df_filtre) > 0
        else 0
    )

    taux_financement = (
        df_filtre[
            "taux_financement_pct"
        ]
        .mean()
        if len(df_filtre) > 0
        else 0
    )


    st.markdown("## Tableau de bord exécutif")

    k1, k2, k3, k4, k5 = (
        st.columns(5)
    )

    with k1:
        carte_kpi(
            "Volume financier",
            format_euros(volume_total),
            "Production cumulée"
        )

    with k2:
        carte_kpi(
            "Ventes",
            format_nombre(ventes_total),
            "Volume commercial"
        )

    with k3:
        carte_kpi(
            "Contrats financés",
            format_nombre(contrats_total),
            "Financements conclus"
        )

    with k4:
        carte_kpi(
            "Taux de financement",
            f"{taux_financement:.1f} %",
            "Moyenne"
        )

    with k5:
        carte_kpi(
            "Objectifs atteints",
            f"{objectif_pct:.1f} %",
            "Part des observations"
        )


    st.write("")

    region_resume = (
        df_filtre.groupby("region", as_index=False)
        .agg(
            volume=("chiffre_affaires_eur", "sum"),
            ventes=("nb_ventes", "sum"),
            taux=("taux_financement_pct", "mean")
        )
        .sort_values("volume", ascending=False)
    )

    reseau_resume = (
        df_filtre.groupby("reseau", as_index=False)
        .agg(
            volume=("chiffre_affaires_eur", "sum"),
            ventes=("nb_ventes", "sum"),
            taux=("taux_financement_pct", "mean")
        )
        .sort_values("volume", ascending=False)
    )

    if not region_resume.empty and not reseau_resume.empty:
        meilleure_region = region_resume.iloc[0]
        meilleur_reseau = reseau_resume.iloc[0]

        st.markdown(
            f"""
<div class="insight-grid">
    <div class="insight-card">
        <div class="insight-label">Région leader</div>
        <div class="insight-value">{meilleure_region['region']}</div>
        <div class="insight-note">{format_euros(meilleure_region['volume'])} de volume financier sur le périmètre filtré.</div>
    </div>
    <div class="insight-card">
        <div class="insight-label">Réseau leader</div>
        <div class="insight-value">{meilleur_reseau['reseau']}</div>
        <div class="insight-note">{format_euros(meilleur_reseau['volume'])} et {format_nombre(meilleur_reseau['ventes'])} ventes.</div>
    </div>
    <div class="insight-card">
        <div class="insight-label">Lecture rapide</div>
        <div class="insight-value">{objectif_pct:.1f} % d'objectifs atteints</div>
        <div class="insight-note">Indicateur global calculé sur les observations actuellement sélectionnées.</div>
    </div>
</div>
""",
            unsafe_allow_html=True
        )

        diagnostic = diagnostic_executif(
            region_resume,
            reseau_resume,
            objectif_pct
        )

        st.markdown(
            f"""
<div class="comment-card">
    <b>Diagnostic exécutif :</b><br>
    {diagnostic}
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # ÉVOLUTION MENSUELLE + DONUT
    # --------------------------------------------------------

    evolution = (
        df_filtre
        .groupby("date_observation")[
            "chiffre_affaires_eur"
        ]
        .sum()
        .reset_index()
    )


    c1, c2 = st.columns(
        [1.65, 0.75]
    )


    with c1:

        st.markdown(
            "### Tendance mensuelle"
        )

        fig_evolution = px.line(
            evolution,
            x="date_observation",
            y="chiffre_affaires_eur",
            markers=True,
            color_discrete_sequence=["#0072CE"]
        )

        fig_evolution.update_traces(
            line=dict(width=3, shape="spline"),
            marker=dict(size=6, color="#0A1F44"),
            fill="tozeroy",
            fillcolor="rgba(0, 114, 206, 0.08)"
        )

        fig_evolution.update_layout(
            xaxis_title="",
            yaxis_title="Volume financier (€)",
            hovermode="x unified"
        )

        theme_figure(fig_evolution, hauteur=390)

        st.plotly_chart(
            fig_evolution,
            use_container_width=True
        )


    with c2:

        st.markdown(
            "### Objectifs atteints"
        )

        atteints = (
            df_filtre["objectif_atteint"]
            .value_counts()
        )

        valeur_non = int(
            atteints.get(0, 0)
        )

        valeur_oui = int(
            atteints.get(1, 0)
        )

        fig_objectif = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Non atteint",
                        "Atteint"
                    ],
                    values=[
                        valeur_non,
                        valeur_oui
                    ],
                    hole=0.68,
                    marker=dict(
                        colors=["#E4E9F2", "#0072CE"]
                    ),
                    textfont=dict(family="Inter, sans-serif")
                )
            ]
        )

        fig_objectif.update_layout(
            showlegend=True
        )

        theme_figure(fig_objectif, hauteur=390)

        st.plotly_chart(
            fig_objectif,
            use_container_width=True
        )


    # --------------------------------------------------------
    # RÉGIONS + RÉSEAUX
    # --------------------------------------------------------

    col_region, col_reseau = (
        st.columns(2)
    )


    with col_region:

        st.markdown(
            "### Performance régionale"
        )

        region_data = (
            df_filtre
            .groupby("region")[
                "chiffre_affaires_eur"
            ]
            .sum()
            .reset_index()
            .sort_values(
                "chiffre_affaires_eur",
                ascending=True
            )
        )

        fig_region = px.bar(
            region_data,
            x="chiffre_affaires_eur",
            y="region",
            orientation="h",
            color="chiffre_affaires_eur",
            color_continuous_scale=PALETTE_SEQUENTIELLE
        )

        fig_region.update_layout(
            xaxis_title="Volume financier (€)",
            yaxis_title="",
            coloraxis_showscale=False
        )

        fig_region.update_traces(marker_line_width=0)

        theme_figure(fig_region, hauteur=420)

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )


    with col_reseau:

        st.markdown(
            "### Performance par marque"
        )

        reseau_data = (
            df_filtre
            .groupby("reseau")[
                "chiffre_affaires_eur"
            ]
            .sum()
            .reset_index()
            .sort_values(
                "chiffre_affaires_eur",
                ascending=False
            )
        )

        fig_reseau = px.bar(
            reseau_data,
            x="reseau",
            y="chiffre_affaires_eur",
            color="reseau",
            color_discrete_sequence=PALETTE_CATEGORIES
        )

        fig_reseau.update_layout(
            xaxis_title="",
            yaxis_title="Volume financier (€)",
            showlegend=False
        )

        fig_reseau.update_traces(marker_line_width=0)

        theme_figure(fig_reseau, hauteur=420)

        st.plotly_chart(
            fig_reseau,
            use_container_width=True
        )


    # --------------------------------------------------------
    # COMPARATEUR DE PERFORMANCE
    # --------------------------------------------------------

    st.markdown("## Comparateur de performance")

    st.markdown(
        """
<div class="compare-box">
    <div class="compare-title">Comparer deux périmètres</div>
    <div class="compare-sub">Sélectionnez deux régions ou deux réseaux pour comparer leurs résultats et obtenir une interprétation automatique.</div>
</div>
""",
        unsafe_allow_html=True
    )

    mode_comparaison = st.radio(
        "Type de comparaison",
        ["Régions", "Réseaux"],
        horizontal=True,
        key="mode_comparaison"
    )

    if mode_comparaison == "Régions":
        valeurs_compare = sorted(df_filtre["region"].dropna().unique().tolist())
        champ_compare = "region"
    else:
        valeurs_compare = sorted(df_filtre["reseau"].dropna().unique().tolist())
        champ_compare = "reseau"

    if len(valeurs_compare) >= 2:
        ccmp1, ccmp2 = st.columns(2)

        with ccmp1:
            choix_a = st.selectbox(
                "Périmètre A",
                valeurs_compare,
                index=0,
                key=f"compare_a_{mode_comparaison}"
            )

        with ccmp2:
            choix_b = st.selectbox(
                "Périmètre B",
                valeurs_compare,
                index=1,
                key=f"compare_b_{mode_comparaison}"
            )

        data_a = df_filtre[df_filtre[champ_compare] == choix_a]
        data_b = df_filtre[df_filtre[champ_compare] == choix_b]

        vol_a = float(data_a["chiffre_affaires_eur"].sum())
        vol_b = float(data_b["chiffre_affaires_eur"].sum())
        ventes_a = float(data_a["nb_ventes"].sum())
        ventes_b = float(data_b["nb_ventes"].sum())
        contrats_a = float(data_a["nb_contrats_financement"].sum())
        contrats_b = float(data_b["nb_contrats_financement"].sum())
        taux_a = float(data_a["taux_financement_pct"].mean()) if len(data_a) else 0
        taux_b = float(data_b["taux_financement_pct"].mean()) if len(data_b) else 0
        objectif_a = float(data_a["objectif_atteint"].mean() * 100) if len(data_a) else 0
        objectif_b = float(data_b["objectif_atteint"].mean() * 100) if len(data_b) else 0

        comp_df = pd.DataFrame({
            "Périmètre": [choix_a, choix_b],
            "Volume financier": [vol_a, vol_b],
            "Ventes": [ventes_a, ventes_b],
            "Contrats": [contrats_a, contrats_b],
            "Taux financement": [taux_a, taux_b],
            "Objectifs atteints": [objectif_a, objectif_b]
        })

        kca, kcb = st.columns(2)

        with kca:
            st.markdown(f"### {choix_a}")
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                carte_kpi("Volume", format_euros(vol_a), "Volume financier")
            with ca2:
                carte_kpi("Ventes", format_nombre(ventes_a), "Cumul")
            with ca3:
                carte_kpi("Objectifs", f"{objectif_a:.1f} %", "Taux d'atteinte")

        with kcb:
            st.markdown(f"### {choix_b}")
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                carte_kpi("Volume", format_euros(vol_b), "Volume financier")
            with cb2:
                carte_kpi("Ventes", format_nombre(ventes_b), "Cumul")
            with cb3:
                carte_kpi("Objectifs", f"{objectif_b:.1f} %", "Taux d'atteinte")

        fig_compare = px.bar(
            comp_df,
            x="Périmètre",
            y="Volume financier",
            color="Périmètre",
            text_auto=".3s",
            color_discrete_sequence=PALETTE_CATEGORIES
        )
        fig_compare.update_layout(
            xaxis_title="",
            yaxis_title="Volume financier (€)",
            showlegend=False
        )
        fig_compare.update_traces(marker_line_width=0)
        theme_figure(fig_compare, hauteur=360)
        st.plotly_chart(fig_compare, use_container_width=True)

        interpretation = texte_comparaison(
            choix_a, choix_b,
            vol_a, vol_b,
            ventes_a, ventes_b,
            taux_a, taux_b
        )

        st.markdown(
            f"""
<div class="comment-card">
    <b>Interprétation automatique :</b><br>
    {interpretation}
</div>
""",
            unsafe_allow_html=True
        )

        tableau_compare = comp_df.copy()
        tableau_compare["Volume financier"] = tableau_compare["Volume financier"].map(format_euros)
        tableau_compare["Ventes"] = tableau_compare["Ventes"].map(format_nombre)
        tableau_compare["Contrats"] = tableau_compare["Contrats"].map(format_nombre)
        tableau_compare["Taux financement"] = tableau_compare["Taux financement"].map(lambda x: f"{x:.1f} %")
        tableau_compare["Objectifs atteints"] = tableau_compare["Objectifs atteints"].map(lambda x: f"{x:.1f} %")

        with st.expander("Voir le détail de la comparaison", expanded=False):
            st.dataframe(tableau_compare, use_container_width=True, hide_index=True)

    else:
        st.info("Au moins deux périmètres sont nécessaires pour effectuer une comparaison.")

    st.markdown("## Classement des meilleures performances")

    rank_region = region_resume.head(3).reset_index(drop=True)

    if len(rank_region) > 0:
        rank_cols = st.columns(len(rank_region))
        for idx, (_, row) in enumerate(rank_region.iterrows()):
            with rank_cols[idx]:
                st.markdown(
                    f"""
<div class="rank-card">
    <div class="rank-pos">{idx + 1}</div>
    <div class="rank-name">{row['region']}</div>
    <div class="rank-value">{format_euros(row['volume'])}</div>
    <div class="rank-value">{format_nombre(row['ventes'])} ventes</div>
</div>
""",
                    unsafe_allow_html=True
                )

    if len(region_resume) >= 2 and len(reseau_resume) >= 2:
        region_gap = variation_pct(
            region_resume.iloc[0]["volume"],
            region_resume.iloc[-1]["volume"]
        )
        reseau_gap = variation_pct(
            reseau_resume.iloc[0]["volume"],
            reseau_resume.iloc[-1]["volume"]
        )

        st.markdown(
            f"""
<div class="decision-grid">
    <div class="decision-card decision-good">
        <div class="decision-title">Opportunité d'analyse</div>
        <div class="decision-text">
            L'écart entre la première et la dernière région atteint environ
            <b>{abs(region_gap):.1f} %</b>. Ce contraste peut orienter une analyse
            plus détaillée des différences d'activité commerciale.
        </div>
    </div>
    <div class="decision-card decision-warn">
        <div class="decision-title">Point d'attention</div>
        <div class="decision-text">
            L'écart entre le réseau le plus et le moins contributeur atteint environ
            <b>{abs(reseau_gap):.1f} %</b>. Cette information doit être interprétée
            avec le contexte réseau et les volumes d'activité associés.
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # RELATION LEADS / PERFORMANCE
    # --------------------------------------------------------

    st.markdown(
        "### Relation entre leads et volume financier"
    )

    fig_scatter = px.scatter(
        df_filtre,
        x="nb_leads",
        y="chiffre_affaires_eur",
        color="reseau",
        size="nb_ventes",
        hover_data=[
            "region",
            "private_fleet",
            "nb_ventes"
        ],
        opacity=0.75,
        color_discrete_sequence=PALETTE_CATEGORIES
    )

    fig_scatter.update_layout(
        xaxis_title="Nombre de leads",
        yaxis_title="Volume financier (€)"
    )

    fig_scatter.update_traces(
        marker=dict(line=dict(width=0.5, color="white"))
    )

    theme_figure(fig_scatter, hauteur=470)

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    corr_leads = df_filtre["nb_leads"].corr(df_filtre["chiffre_affaires_eur"])

    if pd.notna(corr_leads):
        if corr_leads >= 0.7:
            lecture_corr = "forte relation positive"
        elif corr_leads >= 0.4:
            lecture_corr = "relation positive modérée"
        elif corr_leads > 0:
            lecture_corr = "relation positive faible"
        else:
            lecture_corr = "relation faible ou négative"

        st.markdown(
            f"""
<div class="comment-card">
    <b>Lecture du graphique :</b>
    le nombre de leads présente une <b>{lecture_corr}</b> avec le volume financier
    sur le périmètre affiché (corrélation ≈ <b>{corr_leads:.2f}</b>).
    Cette relation décrit les données simulées et ne constitue pas une causalité.
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # DONNÉES
    # --------------------------------------------------------

    with st.expander(
        "Voir les données détaillées",
        expanded=False
    ):

        colonnes = [
            "date_observation",
            "region",
            "reseau",
            "private_fleet",
            "nb_leads",
            "nb_ventes",
            "nb_contrats_financement",
            "taux_financement_pct",
            "chiffre_affaires_eur",
            "objectif_atteint"
        ]

        st.dataframe(
            df_filtre[colonnes],
            use_container_width=True,
            height=430
        )


        csv = (
            df_filtre
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.download_button(
            "Télécharger l'extraction CSV",
            csv,
            "vwfs_donnees_filtrees.csv",
            "text/csv"
        )


# ============================================================
# FONCTION FORMULAIRE SCÉNARIO
# ============================================================

def saisir_scenario(prefix):

    st.markdown(
        '<span class="model-badge">'
        'SCÉNARIO COMMERCIAL'
        '</span>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)


    with c1:

        annee = st.selectbox(
            "Année",
            sorted(
                df["annee"].unique()
            ),
            key=f"{prefix}_annee"
        )

        mois = st.selectbox(
            "Mois",
            range(1, 13),
            key=f"{prefix}_mois"
        )

        trimestre = (
            trimestre_depuis_mois(
                mois
            )
        )

        st.text_input(
            "Trimestre",
            trimestre,
            disabled=True,
            key=f"{prefix}_trimestre"
        )

        region = st.selectbox(
            "Région",
            sorted(
                df["region"].unique()
            ),
            key=f"{prefix}_region"
        )

        reseau = st.selectbox(
            "Réseau",
            sorted(
                df["reseau"].unique()
            ),
            key=f"{prefix}_reseau"
        )

        segment = st.selectbox(
            "Segment",
            sorted(
                df["private_fleet"].unique()
            ),
            key=f"{prefix}_segment"
        )


    with c2:

        commerciaux = st.number_input(
            "Nombre de commerciaux",
            min_value=1,
            value=13,
            key=f"{prefix}_com"
        )

        anciennete = st.number_input(
            "Ancienneté moyenne (mois)",
            min_value=0.0,
            value=60.0,
            key=f"{prefix}_anciennete"
        )

        budget = st.number_input(
            "Budget marketing (€)",
            min_value=0.0,
            value=14000.0,
            step=500.0,
            key=f"{prefix}_budget"
        )

        leads = st.number_input(
            "Nombre de leads",
            min_value=0,
            value=260,
            key=f"{prefix}_leads"
        )

        satisfaction = st.slider(
            "Satisfaction client (%)",
            0.0,
            100.0,
            90.0,
            key=f"{prefix}_sat"
        )

        electrique = st.slider(
            "Part électrifiée (%)",
            0.0,
            100.0,
            25.0,
            key=f"{prefix}_elec"
        )


    with c3:

        taux = st.number_input(
            "Taux d'intérêt moyen (%)",
            min_value=0.0,
            value=5.0,
            step=0.1,
            key=f"{prefix}_taux"
        )

        duree = st.number_input(
            "Durée moyenne (mois)",
            min_value=1.0,
            value=48.0,
            key=f"{prefix}_duree"
        )

        montant = st.number_input(
            "Montant financé moyen (€)",
            min_value=0.0,
            value=35000.0,
            step=500.0,
            key=f"{prefix}_montant"
        )

        saison = st.selectbox(
            "Saison",
            sorted(
                df["saison"].unique()
            ),
            key=f"{prefix}_saison"
        )

        indice = st.number_input(
            "Indice de marché",
            min_value=0.0,
            value=100.0,
            step=1.0,
            key=f"{prefix}_indice"
        )


    return {
        "annee": annee,
        "mois": mois,
        "trimestre": trimestre,
        "region": region,
        "reseau": reseau,
        "private_fleet": segment,
        "nb_commerciaux": commerciaux,
        "anciennete_moyenne_equipe_mois": anciennete,
        "budget_marketing_eur": budget,
        "nb_leads": leads,
        "satisfaction_client_pct": satisfaction,
        "part_electrifiee_pct": electrique,
        "taux_interet_moyen_pct": taux,
        "duree_moyenne_mois": duree,
        "montant_finance_moyen_eur": montant,
        "saison": saison,
        "indice_marche": indice
    }


# ============================================================
# ONGLET 2 - RÉGRESSION
# ============================================================

with tab2:

    st.markdown(
        "## Prévision du volume financier"
    )

    st.markdown(
        """
        <div class="section-card">
        Le modèle Random Forest utilise les caractéristiques
        du scénario commercial pour estimer le niveau de
        production financière attendu.
        </div>
        """,
        unsafe_allow_html=True
    )


    with st.form(
        "form_regression"
    ):

        scenario_reg = saisir_scenario(
            "reg"
        )


        st.markdown(
            "### Objectif financier"
        )

        objectif_financier = (
            st.number_input(
                "Objectif à comparer (€)",
                min_value=0.0,
                value=1500000.0,
                step=10000.0
            )
        )


        lancer_reg = (
            st.form_submit_button(
                "Lancer la simulation",
                type="primary",
                use_container_width=True
            )
        )


    if lancer_reg:

        X_reg = pd.DataFrame(
            [scenario_reg]
        )

        prediction = float(
            modele_regression
            .predict(X_reg)[0]
        )

        ecart = (
            prediction
            - objectif_financier
        )

        taux_ecart = (
            ecart
            / objectif_financier
            * 100
            if objectif_financier > 0
            else 0
        )


        st.markdown(
            """
            <div class="result-card">
            <span class="model-badge">
            RÉSULTAT DE LA SIMULATION
            </span>
            </div>
            """,
            unsafe_allow_html=True
        )


        r1, r2, r3 = st.columns(3)


        with r1:

            carte_kpi(
                "Prévision",
                format_euros(
                    prediction
                ),
                "Random Forest"
            )


        with r2:

            carte_kpi(
                "Objectif",
                format_euros(
                    objectif_financier
                ),
                "Valeur cible"
            )


        with r3:

            carte_kpi(
                "Écart",
                format_euros(
                    ecart
                ),
                f"{taux_ecart:+.1f} %"
            )


        comparaison = pd.DataFrame(
            {
                "Indicateur": [
                    "Prévision",
                    "Objectif"
                ],
                "Montant": [
                    prediction,
                    objectif_financier
                ]
            }
        )

        fig_comparaison = px.bar(
            comparaison,
            x="Indicateur",
            y="Montant",
            text_auto=".3s",
            color="Indicateur",
            color_discrete_map={
                "Prévision": "#0072CE",
                "Objectif": "#0A1F44"
            }
        )

        fig_comparaison.update_layout(
            yaxis_title="Montant (€)",
            xaxis_title="",
            showlegend=False
        )

        fig_comparaison.update_traces(
            marker_line_width=0,
            textfont=dict(family="Space Grotesk, sans-serif", color="white")
        )

        theme_figure(fig_comparaison, hauteur=350)

        st.plotly_chart(
            fig_comparaison,
            use_container_width=True
        )


        if prediction >= objectif_financier:

            st.success(
                "La prévision se situe au-dessus "
                "de l'objectif renseigné."
            )

        else:

            st.warning(
                "La prévision se situe en dessous "
                "de l'objectif renseigné."
            )

        commentaire_reg = commentaire_scenario_regression(
            prediction,
            objectif_financier,
            taux_ecart
        )

        st.markdown(
            f"""
<div class="decision-card decision-blue">
    <div class="decision-title">Interprétation décisionnelle</div>
    <div class="decision-text">{commentaire_reg}</div>
</div>
""",
            unsafe_allow_html=True
        )

        st.caption(
            "Résultat indicatif produit par un modèle "
            "entraîné sur des données simulées."
        )


# ============================================================
# ONGLET 3 - CLASSIFICATION
# ============================================================

with tab3:

    st.markdown(
        "## Probabilité d'atteinte de l'objectif"
    )

    st.markdown(
        """
        <div class="section-card">
        La régression logistique estime la probabilité
        qu'un scénario commercial atteigne les objectifs
        définis.
        </div>
        """,
        unsafe_allow_html=True
    )


    with st.form(
        "form_classification"
    ):

        scenario_class = saisir_scenario(
            "class"
        )

        o1, o2 = st.columns(2)


        with o1:

            objectif_ventes = (
                st.number_input(
                    "Objectif de ventes",
                    min_value=1,
                    value=50
                )
            )


        with o2:

            objectif_ca = (
                st.number_input(
                    "Objectif financier (€)",
                    min_value=0.0,
                    value=1500000.0,
                    step=10000.0
                )
            )


        lancer_class = (
            st.form_submit_button(
                "Évaluer le scénario",
                type="primary",
                use_container_width=True
            )
        )


    if lancer_class:

        scenario_class[
            "objectif_ventes"
        ] = objectif_ventes

        scenario_class[
            "objectif_ca_eur"
        ] = objectif_ca


        X_class = pd.DataFrame(
            [scenario_class]
        )


        classe = (
            modele_classification
            .predict(X_class)[0]
        )


        proba = (
            modele_classification
            .predict_proba(X_class)[0]
        )


        classes_modele = list(
            modele_classification
            .named_steps["model"]
            .classes_
        )


        probabilite = (
            proba[
                classes_modele.index(1)
            ]
            * 100
        )


        res1, res2 = (
            st.columns(
                [0.9, 1.4]
            )
        )


        with res1:

            carte_kpi(
                "Probabilité estimée",
                f"{probabilite:.1f} %",
                (
                    "Classe : atteint"
                    if classe == 1
                    else "Classe : non atteint"
                )
            )


        with res2:

            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=probabilite,
                    number={
                        "suffix": "%",
                        "font": {"family": "Space Grotesk, sans-serif", "color": "#0A1F44"}
                    },
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickcolor": "#93A2B8"
                        },
                        "bar": {
                            "thickness": 0.30,
                            "color": "#0072CE"
                        },
                        "bgcolor": "white",
                        "borderwidth": 0,
                        "steps": [
                            {
                                "range": [
                                    0,
                                    40
                                ],
                                "color": "#FBEAE8"
                            },
                            {
                                "range": [
                                    40,
                                    70
                                ],
                                "color": "#FCF1DF"
                            },
                            {
                                "range": [
                                    70,
                                    100
                                ],
                                "color": "#E5F5EC"
                            }
                        ]
                    }
                )
            )

            fig_gauge.update_layout(
                margin=dict(
                    l=30,
                    r=30,
                    t=25,
                    b=10
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif")
            )

            fig_gauge.update_layout(height=270)

            st.plotly_chart(
                fig_gauge,
                use_container_width=True
            )


        if classe == 1:

            st.success(
                "Tendance favorable : le modèle classe "
                "le scénario parmi les objectifs "
                "susceptibles d'être atteints."
            )

        else:

            st.warning(
                "Tendance défavorable : le modèle classe "
                "le scénario parmi les objectifs "
                "susceptibles de ne pas être atteints."
            )


        if probabilite < 40:

            st.info(
                "Signal faible : une analyse des leviers "
                "commerciaux peut être utile."
            )

        elif probabilite < 70:

            st.info(
                "Zone intermédiaire : le scénario nécessite "
                "une analyse complémentaire."
            )

        else:

            st.info(
                "Signal favorable : la probabilité estimée "
                "est relativement élevée."
            )

        commentaire_class = commentaire_classification(probabilite)

        st.markdown(
            f"""
<div class="decision-card decision-blue">
    <div class="decision-title">Lecture du scénario</div>
    <div class="decision-text">{commentaire_class}</div>
</div>
""",
            unsafe_allow_html=True
        )

        st.caption(
            "Cette probabilité est une aide à la décision. "
            "Elle ne constitue pas une certitude."
        )


# ============================================================
# ONGLET 4 - MÉTHODOLOGIE
# ============================================================

with tab4:

    st.markdown(
        "## Modèles, performances & cadre d'utilisation"
    )


    m1, m2, m3 = st.columns(3)


    with m1:

        st.markdown(
            """
            <div class="section-card model-card">
            <span class="model-badge">
            RÉGRESSION
            </span>

            <h3>Random Forest</h3>

            <b>R² test :</b> 0,9356<br>
            <b>RMSE :</b> 181 680,70 €<br>
            <b>MAE :</b> 129 389,74 €<br>
            <b>MSE :</b> 3,300788 × 10¹⁰
            </div>
            """,
            unsafe_allow_html=True
        )


    with m2:

        st.markdown(
            """
            <div class="section-card model-card">
            <span class="model-badge">
            CLASSIFICATION
            </span>

            <h3>Logistic Regression</h3>

            <b>Accuracy :</b> 62,90 %<br>
            <b>Precision :</b> 30,54 %<br>
            <b>Recall :</b> 63,29 %<br>
            <b>F1-score :</b> 41,19 %
            </div>
            """,
            unsafe_allow_html=True
        )


    with m3:

        st.markdown(
            """
            <div class="section-card model-card">
            <span class="model-badge">
            DEEP LEARNING
            </span>

            <h3>MLP</h3>

            <b>Architecture :</b> 128 → 64 → 32 → 1<br>
            <b>R² test :</b> 0,9316<br>
            <b>RMSE :</b> 187 366,80 €<br>
            <b>MAE :</b> 132 011,97 €
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "### Données utilisées"
    )

    d1, d2, d3, d4 = (
        st.columns(4)
    )


    with d1:
        carte_kpi(
            "Observations",
            "3 360",
            "Dataset simulé"
        )

    with d2:
        carte_kpi(
            "Variables",
            "29",
            "Dimensions métier"
        )

    with d3:
        carte_kpi(
            "Régions",
            "8",
            "Périmètre simulé"
        )

    with d4:
        carte_kpi(
            "Réseaux",
            "5",
            "VW / Audi / Skoda / Seat / Cupra"
        )


    st.write("")


    st.markdown(
        "### Principes d'utilisation"
    )

    st.markdown(
        """
        <div class="section-card">

        - Les données du prototype sont **simulées**.
        - Aucune donnée personnelle directement identifiante
          n'est utilisée.
        - Les résultats produits sont des **estimations**.
        - Les prédictions doivent rester sous
          **supervision humaine**.
        - Aucun résultat ne doit déclencher seul une
          décision commerciale.
        - Avant une mise en production, les modèles devraient
          être validés sur des données historiques réelles.

        </div>
        """,
        unsafe_allow_html=True
    )


    st.warning(
        "Prototype expérimental — les performances affichées "
        "ne doivent pas être assimilées à des performances "
        "réelles de Volkswagen Financial Services."
    )


# ============================================================
# PIED DE PAGE
# ============================================================

st.divider()

st.caption(
    "Prototype Data & Intelligence Artificielle • "
    "Application d'aide à la décision"
)