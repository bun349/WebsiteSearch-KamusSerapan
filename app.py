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
st.set_page_config(page_title="Pencarian Kamus Serapan", layout="centered")

st.title("Sistem Pencarian Kata Serapan")
st.write("Akses data etimologi kata serapan dalam Bahasa Indonesia berbasis *Semantic Web*.")
st.markdown("---")

tab1, tab2 = st.tabs(["Search Bar", "SPARQL Query"])

with tab1:
    st.subheader("Pencarian Kata Cepat")
    kata_kunci = st.text_input("Masukkan kata serapan (contoh: abdomen, kaisar, gratis):", key="search_input")

    if st.button("Cari Kata", type="primary"):
        if kata_kunci.strip() == "":
            st.warning("Silakan masukkan kata kunci terlebih dahulu.")
        else:
            with st.spinner(f"Mencari kata '{kata_kunci}' di database..."):
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
                        st.success(f"Ditemukan {len(df_hasil)} hasil pencarian.")
                        df_display = df_hasil.rename(columns={
                            "kata": "Kata Serapan",
                            "asalBahasa": "Bahasa Sumber",
                            "bentukAsli": "Bentuk Asli",
                            "maknaKata": "Makna"
                        })
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.info(f"Tidak ada data ditemukan untuk kata '{kata_kunci}'.")

with tab2:
    st.subheader("Eksekusi Query SPARQL Manual")
    
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

    query_input = st.text_area("Tulis Query SPARQL kamu di sini:", value=default_query, height=250)

    if st.button("Jalankan Query"):
        if query_input.strip() == "":
            st.warning("Query tidak boleh kosong.")
        else:
            with st.spinner("Mengambil data dari Fuseki..."):
                raw_data = run_sparql_query(query_input)
                
                if raw_data:
                    df_custom = parse_results_to_dataframe(raw_data)
                    
                    if not df_custom.empty:
                        st.success(f"Berhasil memuat {len(df_custom)} data!")
                        st.dataframe(df_custom, use_container_width=True)
                    else:
                        st.warning("Query berhasil dijalankan, tetapi tidak ada data yang cocok atau format kolom berbeda.")

st.markdown("---")
st.caption("Proyek Semantic Web - Kelompok 6")