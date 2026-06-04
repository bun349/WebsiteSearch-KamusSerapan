import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

# 1. Konfigurasi SPARQL Endpoint
# Pastikan server Jena Fuseki sedang berjalan dan nama datasetnya "KamusSerapan"
# Ubah URL ini jika nama dataset kamu berbeda
SPARQL_ENDPOINT = "http://localhost:3030/kamus-serapan/query"

def get_data_from_fuseki(keyword):
    """
    Fungsi untuk mengirim query ke Apache Jena Fuseki 
    dan mengembalikan hasilnya dalam bentuk list of dictionary.
    """
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    
    # Query SPARQL menggunakan REGEX agar pencarian fleksibel (partial match)
    # Gunakan {{ dan }} untuk bagian query agar tidak bentrok dengan f-string Python
    query = f"""
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
      
      # Menyaring hasil berdasarkan kata kunci yang diketik pengguna (i = case insensitive)
      FILTER(REGEX(STR(?kata), "{keyword}", "i"))
    }}
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        data = []
        
        # Mengekstrak hasil query JSON menjadi list Python
        for result in results["results"]["bindings"]:
            data.append({
                "Kata Serapan": result["kata"]["value"],
                "Bahasa Sumber": result["asalBahasa"]["value"],
                "Bentuk Asli": result["bentukAsli"]["value"],
                "Makna": result["maknaKata"]["value"]
            })
        return data
    except Exception as e:
        st.error(f"Gagal terhubung ke SPARQL Endpoint. Pastikan Apache Jena Fuseki berjalan. Detail Error: {e}")
        return []

# 2. Pengaturan UI Streamlit
st.set_page_config(page_title="Pencarian Kamus Serapan", page_icon="📖", layout="centered")

st.title("📖 Sistem Pencarian Kata Serapan")
st.write("Cari etimologi (asal-usul) kata serapan dalam Bahasa Indonesia berbasis *Semantic Web*.")
st.markdown("---")

# Form pencarian
kata_kunci = st.text_input("🔍 Masukkan kata serapan (contoh: abdomen, kaisar, gratis):")

if st.button("Cari", type="primary"):
    if kata_kunci.strip() == "":
        st.warning("Silakan masukkan kata kunci terlebih dahulu.")
    else:
        with st.spinner(f"Mencari kata '{kata_kunci}' di database Semantic Web..."):
            hasil = get_data_from_fuseki(kata_kunci)
            
            if hasil:
                st.success(f"Ditemukan {len(hasil)} hasil pencarian.")
                
                # Menampilkan data menggunakan Pandas DataFrame agar rapi seperti tabel
                df = pd.DataFrame(hasil)
                df.index = df.index + 1  # Index tabel mulai dari 1 (bukan 0)
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"Tidak ada data ditemukan untuk kata '{kata_kunci}'.")

st.markdown("---")
st.caption("Proyek Semantic Web - Endpoint: localhost:3030")