import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from weasyprint import HTML
import base64

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

# --- GESTIONE LINGUA (DEFAULT: ITALIANO) ---
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
    total_thickness = st.number_input(t["total_thickness"], value=50.0, step=5.0, min_value=1.0)
with col_g2:
    hourly_output = st.number_input(t["hourly_output"], value=1000.0, step=100.0, min_value=1.0)

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
    st.error(f"⚠️ Total layer distribution is {total_layer_pct}%. It MUST equal 100%! / La somma deve essere 100%!")

st.markdown("---")

# --- 3. CONFIGURAZIONE MATRICI ESTRUSORI (7 COMPONENTI CIASCUNO) ---
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
        
        total_comp_pct = sum([c["pct_in_layer"] for c in layer_components])
        if abs(total_comp_pct - 100.0) > 0.01 and layer_splits[layer] > 0:
            st.warning(f"⚠️ {layer} components sum up to {total_comp_pct}%. It should be 100% if the layer is active.")
            
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

total_film_density = sum([layer_splits[l] * layer_metrics[l]["density"] for l in layers]) / 100.0

total_material_cost_kg = 0.0
if total_film_density > 0:
    for l in layers:
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

# --- FUNZIONE GENERAZIONE PDF COMACT ED ELIDIBILE SU A4 ---
def generate_pdf():
    # Creazione della tabella di riepilogo globale in HTML
    summary_rows_html = ""
    for l in layers:
        thick_um = total_thickness * (layer_splits[l] / 100.0)
        weight_pct = ((layer_splits[l] * layer_metrics[l]["density"]) / total_film_density) * 100 if total_film_density > 0 else 0
        
        # Estrazione delle ricette interne condensatissime
        comp_details = ""
        for c in recipe_data[l]:
            comp_details += f"• {c['name']}: {c['pct_in_layer']}% (ρ:{c['density']} - €{c['cost']:.2f})<br>"
            
        summary_rows_html += f"""
        <tr>
            <td style="font-weight: bold; background-color: #f9f9f9;">{l}</td>
            <td>{layer_splits[l]:.1f} %</td>
            <td>{thick_um:.2f} µm</td>
            <td>{weight_pct:.1f} %</td>
            <td>€ {layer_metrics[l]['cost_per_kg']:.2f}</td>
            <td style="font-size: 9pt; text-align: left; padding-left: 8px;">{comp_details if comp_details else 'Empty / Vuoto'}</td>
        </tr>
        """

    # Template HTML ad alta densità informativa studiato per un foglio singolo A4
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: A4;
                margin: 12mm 10mm 12mm 10mm;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
                font-size: 10pt;
                line-height: 1.3;
            }}
            .header {{
                border-bottom: 2px solid #002D62;
                padding-bottom: 6px;
                margin-bottom: 12px;
            }}
            .header h1 {{
                font-size: 16pt;
                color: #002D62;
                margin: 0 0 4px 0;
                text-transform: uppercase;
                font-weight: bold;
            }}
            .kpi-container {{
                margin-bottom: 12px;
                background-color: #F0F4F8;
                padding: 10px;
                border-radius: 4px;
                border-left: 4px solid #002D62;
            }}
            .kpi-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .kpi-table td {{
                padding: 4px;
                width: 25%;
                vertical-align: top;
            }}
            .kpi-label {{
                font-size: 8pt;
                text-transform: uppercase;
                color: #555;
                margin-bottom: 2px;
            }}
            .kpi-value {{
                font-size: 13pt;
                font-weight: bold;
                color: #002D62;
            }}
            h2 {{
                font-size: 11pt;
                color: #002D62;
                margin: 10px 0 6px 0;
                border-bottom: 1px solid #ddd;
                padding-bottom: 2px;
            }}
            .main-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
                font-size: 9.5pt;
            }}
            .main-table th {{
                background-color: #002D62;
                color: white;
                font-weight: bold;
                padding: 6px;
                text-align: center;
                font-size: 9pt;
            }}
            .main-table td {{
                border: 1px solid #ddd;
                padding: 5px;
                text-align: center;
                vertical-align: middle;
            }}
            .footer {{
                position: fixed;
                bottom: 0;
                width: 100%;
                border-top: 1px solid #ddd;
                padding-top: 4px;
                font-size: 8pt;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{t['pdf_title']}</h1>
            <div style="font-size: 9pt; color:#666;">Generated via Cast Film Advisor | Live Calculation Matrix</div>
        </div>

        <div class="kpi-container">
            <table class="kpi-table">
                <tr>
                    <td>
                        <div class="kpi-label">{t['cost_kg_film']}</div>
                        <div class="kpi-value">€ {total_material_cost_kg:.3f}</div>
                    </td>
                    <td>
                        <div class="kpi-label">{t['total_hourly_cost']}</div>
                        <div class="kpi-value">€ {hourly_material_cost:,.2f}</div>
                    </td>
                    <td>
                        <div class="kpi-label">{t['total_thickness']}</div>
                        <div class="kpi-value">{total_thickness:.1f} µm</div>
                    </td>
                    <td>
                        <div class="kpi-label">{t['density_calc']}</div>
                        <div class="kpi-value">{total_film_density:.3f} g/cm³</div>
                    </td>
                </tr>
            </table>
        </div>

        <h2>STRUCTURE & COMPONENT RECIPE BREAKDOWN</h2>
        <table class="main-table">
            <thead>
                <tr>
                    <th style="width: 10%;">{t['layer_name']}</th>
                    <th style="width: 10%;">% Geom (Vol)</th>
                    <th style="width: 12%;">Thickness</th>
                    <th style="width: 10%;">% Weight</th>
                    <th style="width: 13%;">Cost (€/kg)</th>
                    <th style="width: 45%;">Dosing Recipe Components (% / Density / Cost)</th>
                </tr>
            </thead>
            <tbody>
                {summary_rows_html}
            </tbody>
        </table>

        <div class="footer">
            Confidential Technical Data Sheet - Formato A4 Ottimizzato per la Stampa Diretto
        </div>
    </body>
    </html>
    """
    # Compilazione tramite WeasyPrint in un oggetto binario
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

# --- AGGIUNTA SEZIONE EXPORT NELL'INTERFACCIA ---
st.markdown("### 🖨️ Export & Print Management")
try:
    pdf_data = generate_pdf()
    st.download_button(
        label=t["btn_pdf"],
        data=pdf_data,
        file_name="9_Layer_Recipe_Report.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Errore durante la compilazione del PDF: {e}")

# --- GRAFICI E TABELLA STANDARD DI STREAMLIT ---
c1, c2 = st.columns([2, 3])
with c1:
    st.subheader(t["layer_thick_table"])
    thickness_data = []
    for l in layers:
        thick_um = total_thickness * (layer_splits[l] / 100.0)
        weight_pct = ((layer_splits[l] * layer_metrics[l]["density"]) / total_film_density) * 100 if total_film_density > 0 else 0
        thickness_data.append({
            t["layer_name"]: l,
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
        x=layers,
        y=layer_thicknesses,
        text=[f"€{c:.2f}/kg" for c in layer_costs],
        textposition='auto',
        marker=dict(color=layer_costs, colorscale='Viridis', showscale=True, colorbar=dict(title="€/kg"))
    ))
    fig.update_layout(yaxis_title="Layer Thickness (µm)", xaxis_title="Film Structure (9 Layers)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
