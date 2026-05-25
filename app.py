import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Calcolatore Costo Film 9-Strati", layout="wide")

# --- DIZIONARIO TRADUZIONI ---
lang_dict = {
    "Italiano": {
        "title": "Calcolatore Costo e Ricetta Film Coestruso a 9 Strati",
        "global_param": "🌐 Parametri Globali del Film e di Produzione",
        "total_thickness": "Spessore Totale Film (µm)",
        "hourly_output": "Portata Oraria Target (kg/h)",
        "layer_dist": "🥞 Configurazione Spessori dei 9 Strati",
        "extruder_config": "🧪 Sistemi di Dosaggio Estrusori (Max 7 Componenti per Strato)",
        "layer_name": "Strato",
        "pct_film": "% del Film",
        "calc_results": "📊 Valutazione Economica e Tecnica",
        "cost_kg_film": "Costo Medio Materiale Film (€/kg)",
        "total_hourly_cost": "Costo Orario Materie Prime (€/h)",
        "density_calc": "Densità Calcolata del Film (g/cm³)",
        "layer_thick_table": "Spessori Calcolati dei Singoli Strati (µm)",
        "component": "Componente",
        "pct_in_layer": "% nello Strato",
        "density": "Densità (g/cm³)",
        "cost_euro_kg": "Costo (€/kg)",
        "btn_pdf": "📄 Genera Report PDF (Pronto per A4)",
        "pdf_title": "REPORT TECNICO - STRUTTURA COESTRUSA 9 STRATI"
    },
    "English": {
        "title": "9-Layer Coextrusion Film Cost & Recipe Calculator",
        "global_param": "🌐 Global Film & Production Parameters",
        "total_thickness": "Total Film Thickness (µm)",
        "hourly_output": "Target Production Output (kg/h)",
        "layer_dist": "🥞 9-Layer Distribution Set-points",
        "extruder_config": "🧪 Extruder Dosing Systems (Max 7 Components per Layer)",
        "layer_name": "Layer",
        "pct_film": "% of Film",
        "calc_results": "📊 Economic & Technical Evaluation",
        "cost_kg_film": "Average Film Material Cost (€/kg)",
        "total_hourly_cost": "Raw Material Hourly Cost (€/h)",
        "density_calc": "Calculated Film Density (g/cm³)",
        "layer_thick_table": "Calculated Layer Thicknesses (µm)",
        "component": "Component",
        "pct_in_layer": "% in Layer",
        "density": "Density (g/cm³)",
        "cost_euro_kg": "Cost (€/kg)",
        "btn_pdf": "📄 Generate PDF Report (A4 Ready)",
        "pdf_title": "TECHNICAL REPORT - 9-LAYER COEXTRUSION STRUCTURE"
    }
}

# --- GESTIONE LINGUA ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "Italiano"

selected_lang = st.sidebar.selectbox("Lingua / Language", ["Italiano", "English"], index=0 if st.session_state['lang'] == "Italiano" else 1)
st.session_state['lang'] = selected_lang
t = lang_dict[st.session_state['lang']]

st.title(t["title"])
st.markdown("---")

# --- 1. PARAMETRI GLOBALI ---
st.header(t["global_param"])
col_g1, col_g2 = st.columns(2)
with col_g1:
    total_thickness = st.number_input(t["total_thickness"], value=60.0, step=5.0, min_value=1.0)
with col_g2:
    hourly_output = st.number_input(t["hourly_output"], value=400.0, step=100.0, min_value=1.0)

st.markdown("---")

# --- 2. DISTRIBUZIONE DEI 9 STRATI (A-I) ---
st.header(t["layer_dist"])
layers = [f"Layer {ch}" for ch in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]]
default_pacts = [15, 10, 10, 10, 10, 10, 10, 10, 15] 

col_layers = st.columns(9)
layer_splits = {}
for i, layer in enumerate(layers):
    with col_layers[i]:
        layer_splits[layer] = st.number_input(f"% {layer}", min_value=0.0, max_value=100.0, value=float(default_pacts[i]), step=1.0)

total_layer_pct = sum(layer_splits.values())
if abs(total_layer_pct - 100.0) > 0.01:
    st.error(f"⚠️ Total layer distribution is {total_layer_pct}%. It MUST equal 100%!")

st.markdown("---")

# --- 3. CONFIGURAZIONE MATRICI ESTRUSORI ---
st.header(t["extruder_config"])

recipe_data = {}
tabs = st.tabs(layers)

for i, layer in enumerate(layers):
    with tabs[i]:
        st.subheader(f"⚙️ Dosing Matrix - {layer} ({layer_splits[layer]}% of film)")
        
        cols_header = st.columns([2, 2, 2, 2])
        cols_header[0].markdown(f"**{t['component']}**")
        cols_header[1].markdown(f"**{t['pct_in_layer']}**")
        cols_header[2].markdown(f"**{t['density']}**")
        cols_header[3].markdown(f"**{t['cost_euro_kg']}**")
        
        layer_components = []
        def_pcts = [100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        def_dens = [0.92, 0.90, 1.14, 1.17, 0.93, 0.92, 0.92]
        def_costs = [1.35, 1.40, 3.60, 8.80, 2.80, 1.35, 1.35]
        
        for comp_idx in range(1, 8):
            row_cols = st.columns([2, 2, 2, 2])
            with row_cols[0]:
                comp_name = st.text_input(f"Name C{comp_idx}", value=f"Mat_C{comp_idx}" if comp_idx == 1 else "", key=f"name_{layer}_{comp_idx}")
            with row_cols[1]:
                comp_pct = row_cols[1].number_input(f"% C{comp_idx}", min_value=0.0, max_value=100.0, value=def_pcts[comp_idx-1], step=5.0, key=f"pct_{layer}_{comp_idx}")
            with row_cols[2]:
                comp_dens = row_cols[2].number_input(f"Density C{comp_idx}", min_value=0.0, value=def_dens[comp_idx-1], format="%.3f", key=f"dens_{layer}_{comp_idx}")
            with row_cols[3]:
                comp_cost = row_cols[3].number_input(f"Cost C{comp_idx}", min_value=0.0, value=def_costs[comp_idx-1], format="%.2f", key=f"cost_{layer}_{comp_idx}")
            
            if comp_pct > 0:
                layer_components.append({
                    "name": comp_name if comp_name else f"Material_{comp_idx}",
                    "pct_in_layer": comp_pct,
                    "density": comp_dens,
                    "cost": comp_cost
                })
        
        recipe_data[layer] = layer_components

# --- 4. ENGINE DI CALCOLO COESTRUSIONE ---
layer_metrics = {}
for layer in layers:
    components = recipe_data[layer]
    if not components:
        layer_metrics[layer] = {"density": 0.0, "cost_per_kg": 0.0}
        continue
    total_pct = sum([c["pct_in_layer"] for c in components])
    if total_pct > 0:
        avg_density = sum([c["pct_in_layer"] * c["density"] for c in components]) / total_pct
        avg_cost_kg = sum([c["pct_in_layer"] * c["cost"] for c in components]) / total_pct
    else:
        avg_density, avg_cost_kg = 0.0, 0.0
    layer_metrics[layer] = {"density": avg_density, "cost_per_kg": avg_cost_kg}

# Densità globale corretta
total_film_density = sum([layer_splits[l] * layer_metrics[l]["density"] for l in layers]) / 100.0

total_material_cost_kg = 0.0
if total_film_density > 0:
    for l in layers:
        # Frazione in peso (split spessore * densità strato) / (100 * densità globale)
        weight_fraction = (layer_splits[l] * layer_metrics[l]["density"]) / (total_film_density * 100.0)
        total_material_cost_kg += weight_fraction * layer_metrics[l]["cost_per_kg"]

hourly_material_cost = hourly_output * total_material_cost_kg

# --- 5. VISUALIZZAZIONE RISULTATI ---
st.markdown("---")
st.header(t["calc_results"])

m1, m2, m3 = st.columns(3)
m1.metric(t["cost_kg_film"], f"€ {total_material_cost_kg:.3f}")
m2.metric(t["density_calc"], f"{total_film_density:.3f} g/cm³")
m3.metric(t["total_hourly_cost"], f"€ {hourly_material_cost:,.2f}")

# --- FUNZIONE GENERAZIONE PDF CON FPDF2 (CORRETTA) ---
def generate_fpdf():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=12, top=12, right=12)
    pdf.add_page()
    
    pdf.set_fill_color(0, 45, 98)
    pdf.rect(12, 12, 186, 18, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(186, 10, f"  {t['pdf_title']}", ln=True, align="L")
    pdf.set_font("Arial", "", 8)
    pdf.cell(186, 2, "   Generated via Cast Film Advisor Matrix Engine", ln=True, align="L")
    pdf.ln(8)
    
    pdf.set_fill_color(240, 244, 248)
    pdf.rect(12, 35, 186, 16, "F")
    pdf.set_text_color(0, 45, 98)
    pdf.set_font("Arial", "B", 10)
    
    pdf.set_y(36)
    pdf.cell(46, 6, f"Cost: EUR {total_material_cost_kg:.3f}/kg", align="C")
    pdf.cell(46, 6, f"Hourly Cost: EUR {hourly_material_cost:,.2f}/h", align="C")
    pdf.cell(46, 6, f"Thick: {total_thickness:.1f} um", align="C")
    pdf.cell(48, 6, f"Density: {total_film_density:.3f} g/cm3", align="C")
    pdf.ln(12)
    
    pdf.set_text_color(0, 45, 98)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(186, 8, "STRUCTURE & COMPONENT RECIPE BREAKDOWN", ln=True)
    pdf.ln(2)
    
    pdf.set_fill_color(0, 45, 98)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 7, "Layer", border=1, align="C", fill=True)
    pdf.cell(15, 7, "% Vol", border=1, align="C", fill=True)
    pdf.cell(20, 7, "Thick (um)", border=1, align="C", fill=True)
    pdf.cell(15, 7, "% Wt", border=1, align="C", fill=True)
    pdf.cell(23, 7, "Cost (EUR)", border=1, align="C", fill=True)
    pdf.cell(98, 7, "Dosing Components Structure", border=1, align="L", fill=True)
    pdf.ln()
    
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial", "", 8.5)
    
    for l in layers:
        thick_um = total_thickness * (layer_splits[l] / 100.0)
        # CALCOLO FRAZIONE IN PESO IN % CORRETTO
        weight_pct = ((layer_splits[l] * layer_metrics[l]["density"]) / (total_film_density * 100.0)) * 100 if total_film_density > 0 else 0
        
        comp_text = ""
        for c in recipe_data[l]:
            comp_text += f"{c['name']}: {c['pct_in_layer']}% | "
        if comp_text.endswith(" | "): 
            comp_text = comp_text[:-3]
            
        pdf.cell(15, 7, l.replace("Layer ", ""), border=1, align="C")
        pdf.cell(15, 7, f"{layer_splits[l]:.1f}", border=1, align="C")
        pdf.cell(20, 7, f"{thick_um:.2f}", border=1, align="C")
        pdf.cell(15, 7, f"{weight_pct:.1f}", border=1, align="C")
        pdf.cell(23, 7, f"{layer_metrics[l]['cost_per_kg']:.2f}", border=1, align="C")
        pdf.cell(98, 7, f" {comp_text[:60]}", border=1, align="L")
        pdf.ln()
        
    return pdf.output()

# --- INTERFACCIA DOWNLOAD ---
st.markdown("### 🖨️ Export & Print Management")
try:
    pdf_bytes = generate_fpdf()
    st.download_button(
        label=t["btn_pdf"],
        data=pdf_bytes,
        file_name="Report_Ricetta_9Strati.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Errore generazione PDF: {e}")

# --- TABELLA E GRAFICI SCREEN ---
c1, c2 = st.columns([2, 3])
with c1:
    st.subheader(t["layer_thick_table"])
    thickness_data = []
    for l in layers:
        thick_um = total_thickness * (layer_splits[l] / 100.0)
        # CORREZIONE FORMULA SCALA TABELLA STREAMLIT
        weight_pct = ((layer_splits[l] * layer_metrics[l]["density"]) / (total_film_density * 100.0)) * 100 if total_film_density > 0 else 0
        
        thickness_data.append({
            t["layer_name"]: l.replace("Layer ", ""),
            "% Vol": f"{layer_splits[l]:.1f} %",
            "Thickness (µm)": f"{thick_um:.2f} µm",
            "Weight %": f"{weight_pct:.1f} %",
            "Cost (€/kg)": f"€ {layer_metrics[l]['cost_per_kg']:.2f}"
        })
    st.table(pd.DataFrame(thickness_data))

with c2:
    st.subheader("Visual Layer Breakdown (Thickness vs Cost)")
    layer_thicknesses = [total_thickness * (layer_splits[l] / 100.0) for l in layers]
    layer_costs = [layer_metrics[l]["cost_per_kg"] for l in layers]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[l.replace("Layer ", "") for l in layers],
        y=layer_thicknesses,
        text=[f"€{c:.2f}/kg" for c in layer_costs],
        textposition='auto',
        marker=dict(color=layer_costs, colorscale='Viridis', showscale=True, colorbar=dict(title="€/kg"))
    ))
    fig.update_layout(yaxis_title="Layer Thickness (µm)", xaxis_title="Film Structure (9 Layers)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
