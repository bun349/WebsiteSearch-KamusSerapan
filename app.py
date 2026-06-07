import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

# 1. Konfigurasi SPARQL Endpoint
SPARQL_ENDPOINT = "http://localhost:3030/kamus-serapan/query"

def run_sparql_query(query):
    """Fungsi universal untuk mengirim query SPARQL ke Apache Jena Fuseki"""
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        st.error(f"Gagal terhubung ke SPARQL Endpoint. Pastikan Apache Jena Fuseki berjalan.\nDetail Error: {e}")
        return None

def parse_results_to_dataframe(results):
    """Mengubah hasil JSON Fuseki menjadi Pandas DataFrame secara dinamis"""
    if not results or "results" not in results or not results["results"]["bindings"]:
        return pd.DataFrame()
        
    vars_list = results["head"]["vars"]
    bindings = results["results"]["bindings"]
    
    data = []
    for binding in bindings:
        row = {}
        for var in vars_list:
            row[var] = binding.get(var, {}).get("value", "")
        data.append(row)
        
    df = pd.DataFrame(data)
    df.index = df.index + 1
    return df

# 2. Pengaturan UI Streamlit
st.set_page_config(
    page_title="Kamus Serapan — Semantic Web",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e2d5;
}

.stApp {
    background: #0f0e0c;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(180,140,60,0.12) 0%, transparent 70%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Cpath d='M0 0h60v60H0z' fill='none'/%3E%3Ccircle cx='30' cy='30' r='0.6' fill='%23b48c3c' fill-opacity='0.18'/%3E%3C/svg%3E");
}

/* ── Header Block ── */
.header-block {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
}

.header-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    color: #b48c3c;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.header-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 900;
    line-height: 1.1;
    color: #f0e8d0;
    margin: 0 0 1rem;
    letter-spacing: -0.02em;
}

.header-title span {
    color: #b48c3c;
}

.header-subtitle {
    font-size: 0.95rem;
    color: #8a8070;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}

.divider {
    border: none;
    border-top: 1px solid rgba(180,140,60,0.2);
    margin: 1.5rem auto;
    max-width: 120px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #1a1914;
    border: 1px solid rgba(180,140,60,0.2);
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    color: #6b6355;
    background: transparent;
    border-radius: 7px;
    padding: 0.5rem 1.4rem;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
    border: none;
}

.stTabs [aria-selected="true"] {
    background: rgba(180,140,60,0.15) !important;
    color: #d4a843 !important;
    border: 1px solid rgba(180,140,60,0.3) !important;
}

.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── Section Labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #b48c3c;
    margin-bottom: 0.4rem;
}

/* ── Input Field ── */
.stTextInput > div > div > input {
    background: #1a1914 !important;
    border: 1px solid rgba(180,140,60,0.25) !important;
    border-radius: 10px !important;
    color: #e8e2d5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(180,140,60,0.6) !important;
    box-shadow: 0 0 0 3px rgba(180,140,60,0.08) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder { color: #4a4535 !important; }

/* ── Text Area ── */
.stTextArea > div > div > textarea {
    background: #1a1914 !important;
    border: 1px solid rgba(180,140,60,0.25) !important;
    border-radius: 10px !important;
    color: #c8bfa8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.7 !important;
    padding: 1rem !important;
    transition: border-color 0.2s ease !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: rgba(180,140,60,0.6) !important;
    box-shadow: 0 0 0 3px rgba(180,140,60,0.08) !important;
    outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #b48c3c 0%, #d4a843 100%) !important;
    color: #0f0e0c !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(180,140,60,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(180,140,60,0.35) !important;
    background: linear-gradient(135deg, #c49e4a 0%, #e0b84e 100%) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── DataFrame ── */
.stDataFrame {
    border: 1px solid rgba(180,140,60,0.2) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.stDataFrame [data-testid="stDataFrameResizable"] {
    border-radius: 12px !important;
    background: #1a1914 !important;
}

/* ── Alert Messages ── */
.stSuccess {
    background: rgba(60,120,60,0.12) !important;
    border: 1px solid rgba(80,160,80,0.25) !important;
    border-radius: 10px !important;
    color: #7dba7d !important;
}

.stWarning {
    background: rgba(180,140,60,0.08) !important;
    border: 1px solid rgba(180,140,60,0.25) !important;
    border-radius: 10px !important;
    color: #c8a84a !important;
}

.stInfo {
    background: rgba(60,100,160,0.1) !important;
    border: 1px solid rgba(80,130,200,0.2) !important;
    border-radius: 10px !important;
    color: #7aaad0 !important;
}

.stError {
    background: rgba(160,60,60,0.1) !important;
    border: 1px solid rgba(200,80,80,0.2) !important;
    border-radius: 10px !important;
    color: #d07a7a !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #b48c3c !important; }

/* ── Footer ── */
.footer-block {
    text-align: center;
    padding: 2rem 0 1rem;
}

.footer-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: #3a3528;
    text-transform: uppercase;
}

.footer-dot {
    color: #b48c3c;
    margin: 0 0.5em;
}

/* ── Subheader override ── */
h2, h3 { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1a1914; }
::-webkit-scrollbar-thumb { background: #3a3020; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #b48c3c; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-block">
    <div class="header-eyebrow">✦ Semantic Web — Kelompok 6 ✦</div>
    <h1 class="header-title">Kamus Kata <span>Serapan</span></h1>
    <p class="header-subtitle">
        Eksplorasi etimologi kata serapan dalam Bahasa Indonesia
        berbasis teknologi <em>Semantic Web</em> & RDF.
    </p>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Pencarian Kata", "SPARQL Query"])

with tab1:
    st.markdown('<p class="section-label">Pencarian Cepat</p>', unsafe_allow_html=True)
    kata_kunci = st.text_input(
        label="kata",
        placeholder="Ketik kata serapan… contoh: abdomen, kaisar, gratis",
        label_visibility="collapsed",
        key="search_input"
    )

    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        cari = st.button("Cari Kata", type="primary", use_container_width=True)

    if cari:
        if kata_kunci.strip() == "":
            st.warning("⚠ Silakan masukkan kata kunci terlebih dahulu.")
        else:
            with st.spinner(f"Mencari '{kata_kunci}'…"):
                search_query = f"""
                PREFIX etimologi: <http://etimologi.id/ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                SELECT ?kata ?asalBahasa ?bentukAsli ?maknaKata
                WHERE {{
                  ?instans a etimologi:KataSerapan ;
                           rdfs:label ?kata ;
                           etimologi:berasalDariBahasa ?bhsNode ;
                           etimologi:memilikiBentukAsal ?asalNode ;
                           etimologi:memilikiMakna ?maknaNode .
                           
                  ?bhsNode rdfs:label ?asalBahasa .
                  ?asalNode rdf:value ?bentukAsli .
                  ?maknaNode rdf:value ?maknaKata .
                  
                  FILTER(REGEX(STR(?kata), "{kata_kunci}", "i"))
                }}
                """
                raw_data = run_sparql_query(search_query)
                
                if raw_data:
                    df_hasil = parse_results_to_dataframe(raw_data)
                    
                    if not df_hasil.empty:
                        st.success(f"✓ Ditemukan **{len(df_hasil)}** hasil untuk kata *{kata_kunci}*.")
                        df_display = df_hasil.rename(columns={
                            "kata": "Kata Serapan",
                            "asalBahasa": "Bahasa Sumber",
                            "bentukAsli": "Bentuk Asli",
                            "maknaKata": "Makna"
                        })
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.info(f"Tidak ada data ditemukan untuk kata **'{kata_kunci}'**.")

with tab2:
    st.markdown('<p class="section-label">Eksekusi Query SPARQL Manual</p>', unsafe_allow_html=True)
    
    default_query = """PREFIX etimologi: <http://etimologi.id/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?kata ?asalBahasa ?bentukAsli
WHERE {
  ?instans a etimologi:KataSerapan ;
           rdfs:label ?kata ;
           etimologi:berasalDariBahasa ?bhsNode ;
           etimologi:memilikiBentukAsal ?asalNode .
  ?bhsNode rdfs:label ?asalBahasa .
  ?asalNode rdf:value ?bentukAsli .
}
LIMIT 10"""

    query_input = st.text_area(
        label="query",
        value=default_query,
        height=260,
        label_visibility="collapsed"
    )

    col_btn2, col_empty2 = st.columns([1, 3])
    with col_btn2:
        jalankan = st.button("Jalankan Query", use_container_width=True)

    if jalankan:
        if query_input.strip() == "":
            st.warning("⚠ Query tidak boleh kosong.")
        else:
            with st.spinner("Mengambil data dari Fuseki…"):
                raw_data = run_sparql_query(query_input)
                
                if raw_data:
                    df_custom = parse_results_to_dataframe(raw_data)
                    
                    if not df_custom.empty:
                        st.success(f"✓ Berhasil memuat **{len(df_custom)}** data.")
                        st.dataframe(df_custom, use_container_width=True)
                    else:
                        st.warning("Query berhasil dijalankan, tetapi tidak ada data yang cocok.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-block">
    <p class="footer-text">
        Proyek Semantic Web
        <span class="footer-dot">◆</span>
        Kelompok 6
        <span class="footer-dot">◆</span>
        Apache Jena Fuseki
    </p>
</div>
""", unsafe_allow_html=True)