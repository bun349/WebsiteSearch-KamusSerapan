import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
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
        if "Peek iterator is already empty" in str(e) or "500" in str(e):
            return {"head": {"vars": []}, "results": {"bindings": []}}
        
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


def tampilkan_graph_kata(kata):
    query_graph = f"""
    PREFIX etimologi: <http://etimologi.id/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?kata ?asalBahasa ?bentukAsli ?makna
    WHERE {{
        ?instans a etimologi:KataSerapan ;
                 rdfs:label ?kata ;
                 etimologi:berasalDariBahasa ?bhsNode ;
                 etimologi:memilikiBentukAsal ?asalNode ;
                 etimologi:memilikiMakna ?maknaNode .

        ?bhsNode rdfs:label ?asalBahasa .
        ?asalNode rdf:value ?bentukAsli .
        ?maknaNode rdf:value ?makna .

        FILTER(REGEX(STR(?kata), "{kata}", "i"))
    }}
    """

    results = run_sparql_query(query_graph)

    if not results:
        return

    bindings = results["results"]["bindings"]

    if len(bindings) == 0:
        st.warning("Graph tidak memiliki data.")
        return

    net = Network(
        height="700px",  
        width="100%",
        directed=True,
        bgcolor="#fcfbfa",
        font_color="#2c2519",
    )

    added_nodes = set()

    for row in bindings:
        kata_serapan = row["kata"]["value"]
        bahasa = row["asalBahasa"]["value"]
        bentuk = row["bentukAsli"]["value"]
        makna = row["makna"]["value"]

        # 1. Node Kata Serapan
        if kata_serapan not in added_nodes:
            net.add_node(
                kata_serapan,
                label=kata_serapan,
                color="#b48c3c",
                shape="box",
                margin=10,
                font={"size": 16, "face": "Courier"},
            )
            added_nodes.add(kata_serapan)

        # 2. Node Bahasa asal
        if bahasa not in added_nodes:
            net.add_node(
                bahasa,
                label=bahasa,
                color="#AED6F1",
                shape="ellipse",
                margin=10,
                font={"size": 14},
            )
            added_nodes.add(bahasa)

        # 3. Node Bentuk Asli
        if bentuk not in added_nodes:
            net.add_node(
                bentuk,
                label=bentuk,
                color="#ABEBC6",
                shape="ellipse",
                margin=10,
                font={"size": 14},
            )
            added_nodes.add(bentuk)

        # 4. Node Makna 
        if makna not in added_nodes:
            net.add_node(
                makna,
                label=makna,
                color="#e5c158",
                shape="box",
                margin=12,
                font={"size": 14},
            )
            added_nodes.add(makna)

        net.add_edge(
            kata_serapan,
            bahasa,
            label="berasal dari",
            color="#b48c3c",
            font={"align": "top", "size": 12},
        )

        net.add_edge(
            kata_serapan,
            bentuk,
            label="bentuk asli",
            color="#b48c3c",
            font={"align": "top", "size": 12},
        )

        net.add_edge(
            kata_serapan,
            makna,
            label="makna",
            color="#b48c3c",
            font={"align": "top", "size": 12},
        )

    net.barnes_hut(
        gravity=-2000, 
        central_gravity=0.1,
        spring_length=200, 
        spring_strength=0.05,
        damping=0.09,
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)

        with open(tmp_file.name, "r", encoding="utf-8") as f:
            html = f.read()

    components.html(html, height=750, scrolling=True)
    

# 2. Pengaturan UI Streamlit
st.set_page_config(
    page_title="Kamus Serapan — Semantic Web",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght=700;900&family=DM+Sans:wght=300;400;500&family=DM+Mono:wght=400;500&display=swap');

/* ── Menghilangkan Header Putih Bawaan Streamlit Teratas ── */
header {
    visibility: hidden !important;
    height: 0px !important;
}

/* ── Global App & Background ── */
.stApp {
    background: #fcfbfa;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(180,140,60,0.08) 0%, transparent 70%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Cpath d='M0 0h60v60H0z' fill='none'/%3E%3Ccircle cx='30' cy='30' r='0.6' fill='%23b48c3c' fill-opacity='0.15'/%3E%3C/svg%3E");
    font-family: 'DM Sans', sans-serif;
}

/* Fix text color globally & rapihkan margin atas pasca header hilang */
.main .block-container {
    color: #2c2519;
    padding-top: 2rem !important;
}

/* ── Header Block ── */
.header-block {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1rem 0 1rem 0;
    width: 100%;
}

.header-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    color: #b48c3c;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    width: 100%;
}

.header-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.2rem, 5vw, 3.2rem);
    font-weight: 900;
    line-height: 1.2;
    color: #1a150e;
    margin: 0 0 0.75rem 0;
    letter-spacing: -0.02em;
    width: 100%;
}

.header-title span {
    color: #b48c3c;
}

.header-subtitle {
    font-size: 0.95rem;
    color: #6b6050;
    font-weight: 300;
    width: 100%;
    margin: 0 auto;
    line-height: 1.6;
}

.divider {
    border: none;
    border-top: 1px solid rgba(180,140,60,0.3);
    margin: 1.5rem auto 2rem auto;
    width: 120px;
}

/* ── Tabs Customization ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f4f1ea;
    border: 1px solid rgba(180,140,60,0.25);
    border-radius: 10px;
    padding: 6px;
    margin-bottom: 2rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    color: #7a6f5d;
    background: transparent;
    border-radius: 7px;
    padding: 0.5rem 1.5rem;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
    border: none;
}

.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #b48c3c !important;
    box-shadow: 0 2px 8px rgba(180,140,60,0.12) !important;
}

.stTabs [data-baseweb="tab-highlight"], 
.stTabs [data-baseweb="tab-border"] { 
    display: none !important; 
}

/* ── Section Labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #b48c3c;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

/* ── Form Inputs ── */
div[data-testid="stTextInput"] input, .stSelectbox div[data-baseweb="select"] {
    background: #ffffff !important;
    border: 1px solid rgba(180,140,60,0.3) !important;
    border-radius: 8px !important;
    color: #2c2519 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Memastikan font pilihan dropdown selectbox selaras */
div[data-baseweb="popover"] ul {
    font-family: 'DM Sans', sans-serif !important;
}

div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 1px solid rgba(180,140,60,0.3) !important;
    border-radius: 8px !important;
    color: #3a3225 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 1rem !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #b48c3c 0%, #d4a843 100%) !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 10px rgba(180,140,60,0.15) !important;
    width: 100%;
}

div[data-testid="stButton"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 15px rgba(180,140,60,0.25) !important;
    background: linear-gradient(135deg, #c49e4a 0%, #e0b84e 100%) !important;
}

/* ── Dataframe Wrapper ── */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(180,140,60,0.2) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    margin-top: 1rem;
}

/* ── Footer ── */
.footer-block {
    text-align: center;
    padding: 3rem 0 1.5rem;
}

.footer-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    color: #a09580;
    text-transform: uppercase;
}

.footer-dot {
    color: #b48c3c;
    margin: 0 0.4em;
}

h2, h3 { display: none !important; }
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
tab1, tab2, tab3 = st.tabs(["Pencarian Kata", "Eksplorasi Data", "SPARQL Query"])

# TAB 1: PENCARIAN KATA
with tab1:
    st.markdown('<p class="section-label">Pencarian Cepat</p>', unsafe_allow_html=True)
    kata_kunci = st.text_input(
        label="kata",
        placeholder="Ketik kata serapan… contoh: abdomen, kaisar, gratis",
        label_visibility="collapsed",
        key="search_input"
    )

    col_btn, col_empty = st.columns([1, 2])
    with col_btn:
        cari = st.button("Cari Kata", type="primary", key="btn_cari")

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
                        st.markdown("### Knowledge Graph")

                        tampilkan_graph_kata(kata_kunci)
                    else:
                        st.info(f"Tidak ada data ditemukan untuk kata **'{kata_kunci}'**.")

# TAB 2: EKSPLORASI DATA (NON-SPARQL)
with tab2:
    st.markdown('<p class="section-label">Menu Eksplorasi</p>', unsafe_allow_html=True)
    
    # Pengguna tinggal memilih lewat dropdown
    pilihan_eksplorasi = st.selectbox(
        label="Menu Eksplorasi", 
        options=["Statistik Bahasa Sumber", "Filter Berdasarkan Negara/Bahasa"],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px dashed rgba(180,140,60,0.3);'>", unsafe_allow_html=True)

    # FITUR 1: STATISTIK BAHASA
    if pilihan_eksplorasi == "Statistik Bahasa Sumber":
        st.markdown("**Statistik Jumlah Kata Serapan Berdasarkan Bahasa Asal**")
        
        if st.button("Tampilkan Statistik", type="primary", key="btn_stats"):
            with st.spinner("Menghitung statistik..."):
                query_stats = """
                PREFIX etimologi: <http://etimologi.id/ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?asalBahasa (COUNT(?instans) AS ?TotalKata)
                WHERE {
                  ?instans a etimologi:KataSerapan ;
                           etimologi:berasalDariBahasa ?bhsNode .
                  ?bhsNode rdfs:label ?asalBahasa .
                }
                GROUP BY ?asalBahasa
                ORDER BY DESC(?TotalKata)
                """
                raw_stats = run_sparql_query(query_stats)
                
                if raw_stats:
                    df_stats = parse_results_to_dataframe(raw_stats)
                    if not df_stats.empty:
                        # Konversi tipe data TotalKata ke numerik untuk chart
                        df_stats["TotalKata"] = pd.to_numeric(df_stats["TotalKata"])
                        
                        col_chart, col_data = st.columns([2, 1])
                        
                        with col_data:
                            df_display = df_stats.rename(columns={"asalBahasa": "Bahasa Sumber", "TotalKata": "Jumlah Kata"})
                            st.dataframe(df_display, use_container_width=True)
                            
                        with col_chart:
                            # Menampilkan Bar Chart bawaan Streamlit
                            st.bar_chart(data=df_stats, x="asalBahasa", y="TotalKata", color="#b48c3c")
                    else:
                        st.info("Belum ada data untuk ditampilkan.")

    # FITUR 2: FILTER NEGARA/BAHASA
    elif pilihan_eksplorasi == "Filter Berdasarkan Negara/Bahasa":
        pilihan_bahasa = st.selectbox(
            label="Pilih Bahasa Asal",
            options=["Belanda", "Arab", "Latin", "Sanskerta", "Portugis", "Tamil"]
        )
        
        if st.button("Tampilkan Data", type="primary", key="btn_filter"):
            with st.spinner(f"Mencari kata serapan dari bahasa {pilihan_bahasa}..."):
                query_filter = f"""
                PREFIX etimologi: <http://etimologi.id/ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                SELECT ?kata ?bentukAsli ?maknaKata
                WHERE {{
                  ?instans a etimologi:KataSerapan ;
                           rdfs:label ?kata ;
                           etimologi:berasalDariBahasa ?bhsNode ;
                           etimologi:memilikiBentukAsal ?asalNode ;
                           etimologi:memilikiMakna ?maknaNode .

                  ?bhsNode rdfs:label ?asalBahasa .
                  FILTER regex(?asalBahasa, "{pilihan_bahasa}", "i")

                  ?asalNode rdf:value ?bentukAsli .
                  ?maknaNode rdf:value ?maknaKata .
                }}
                """
                raw_filter = run_sparql_query(query_filter)
                
                if raw_filter:
                    df_filter = parse_results_to_dataframe(raw_filter)
                    if not df_filter.empty:
                        st.success(f"✓ Ditemukan **{len(df_filter)}** kata serapan dari bahasa **{pilihan_bahasa}**.")
                        df_display = df_filter.rename(columns={
                            "kata": "Kata Serapan",
                            "bentukAsli": "Bentuk Asli",
                            "maknaKata": "Makna"
                        })
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.info(f"Tidak ada data kata serapan dari bahasa **{pilihan_bahasa}**.")

# TAB 3: SPARQL QUERY EDITOR
with tab3: 
    st.markdown(
        '<p class="section-label" style="margin-top:1.5rem;">Editor SPARQL Query</p>',
        unsafe_allow_html=True
    )
    
    query_default = """PREFIX etimologi: <http://etimologi.id/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?kata ?asalBahasa ?bentukAsli ?maknaKata
    WHERE {
    ?instans a etimologi:KataSerapan ;
            rdfs:label ?kata ;
            etimologi:berasalDariBahasa ?bhsNode ;
            etimologi:memilikiBentukAsal ?asalNode ;
            etimologi:memilikiMakna ?maknaNode .

    ?bhsNode rdfs:label ?asalBahasa .
    ?asalNode rdf:value ?bentukAsli .
    ?maknaNode rdf:value ?maknaKata .
    }
    LIMIT 20"""

    query_input = st.text_area(
        label="query",
        value=query_default,
        height=320,
        label_visibility="collapsed"
    )

    col_btn2, col_empty2 = st.columns([1, 2])
    with col_btn2:
        jalankan = st.button("Jalankan Query", key="btn_query")

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