import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="9-Layer Cast/Blown Film Cost Calculator", layout="wide")

# --- DIZIONARIO TRADUZIONI ---
lang_dict = {
    "English": {
        "title": "9-Layer Coextrusion Film Cost & Recipe Calculator",
        "global_param": "🌐 Global Film & Production Parameters",
        "total_thickness": "Total Film Thickness (µm)",
        "hourly_output": "Target Production Output (kg/h)",
        "working_hours": "Annual Operating Hours (h)",
        "layer_dist": "🥞 9-Layer Distribution Set-points",
        "extruder_config": "🧪 Extruder Dosing Systems (Max 7 Components per Layer)",
        "layer_name": "Layer",
        "pct_film": "% of Film",
        "calc_results": "📊 Economic & Technical Evaluation",
        "cost_kg_film": "Average Film Material Cost (€/kg)",
        "total_hourly_cost": "Raw Material Hourly Cost (€/h)",
        "annual_material_cost": "Annual Material Expenditure (€/year)",
        "density_calc": "Calculated Film Density (g/cm³)",
        "layer_thick_table": "Calculated Layer Thicknesses (µm)",
        "component": "Component",
        "pct_in_layer": "% in Layer",
        "density": "Density (g/cm³)",
        "cost_euro_kg": "Cost (€/kg)"
    },
    "Italiano": {
        "title": "Calcolatore Costo e Ricetta Film Coestruso a 9 Strati",
        "global_param": "🌐 Parametri Globali del Film e di Produzione",
        "total_thickness": "Spessore Totale Film (µm)",
        "hourly_output": "Portata Oraria Target (kg/h)",
        "working_hours": "Ore di Lavoro Annue (h)",
        "layer_dist": "🥞 Configurazione Spessori dei 9 Strati",
        "extruder_config": "🧪 Sistemi di Dosaggio Estrusori (Max 7 Componenti per Strato)",
        "layer_name": "Strato",
        "pct_film": "% del Film",
        "calc_results": "📊 Valutazione Economica e Tecnica",
        "cost_kg_film": "Costo Medio Materiale Film (€/kg)",
        "total_hourly_cost": "Costo Orario Materie Prime (€/h)",
        "annual_material_cost": "Spesa Annua Materie Prime (€/anno)",
        "density_calc": "Densità Calcolata del Film (g/cm³)",
        "layer_thick_table": "Spessori Calcolati dei Singoli Strati (µm)",
        "component": "Componente",
        "pct_in_layer": "% nello Strato",
        "density": "Densità (g/cm³)",
        "cost_euro_kg": "Costo (€/kg)"
    }
}

# --- GESTIONE LINGUA ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "English"

selected_lang = st.sidebar.selectbox("Language / Lingua", ["English", "Italiano"], index=0 if st.session_state['lang'] == "English" else 1)
st.session_state['lang'] = selected_lang
t = lang_dict[st.session_state['lang']]

st.title(t["title"])
st.markdown("---")

# --- 1. PARAMETRI GLOBALI ---
st.header(t["global_param"])
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    total_thickness = st.number_input(t["total_thickness"], value=50.0, step=5.0, min_value=1.0)
with col_g2:
    hourly_output = st.number_input(t["hourly_output"], value=1000.0, step=100.0, min_value=1.0)
with col_g3:
    working_hours = st.number_input(t["working_hours"], value=7500, step=100, min_value=1)

st.markdown("---")

# --- 2. DISTRIBUZIONE DEI 9 STRATI ---
st.header(t["layer_dist"])
layers = [f"Layer {i}" for i in range(1, 10)]
default_pacts = [15, 10, 10, 10, 10, 10, 10, 10, 15] # Default simmetrico barriera standard

col_layers = st.columns(9)
layer_splits = {}
for i, layer in enumerate(layers):
    with col_layers[i]:
        layer_splits[layer] = st.number_input(f"% {layer}", min_value=0.0, max_value=100.0, value=float(default_pacts[i]), step=1.0)

total_layer_pct = sum(layer_splits.values())
if abs(total_layer_pct - 100.0) > 0.01:
    st.error(f"⚠️ Total layer distribution is {total_layer_pct}%. It MUST equal 100%!")

st.markdown("---")

# --- 3. CONFIGURAZIONE MATRICI ESTRUSORI (7 COMPONENTI CIASCUNO) ---
st.header(t["extruder_config"])

recipe_data = {}

# Creiamo tab interattive per non affollare la schermata, una per ogni estrusore
tabs = st.tabs(layers)

for i, layer in enumerate(layers):
    with tabs[i]:
        st.subheader(f"⚙️ Dosing Matrix - {layer} ({layer_splits[layer]}% of film)")
        
        # Generiamo la griglia per i 7 componenti del sistema di dosaggio (es. Gravimetrico)
        cols_header = st.columns([2, 2, 2, 2])
        cols_header[0].markdown(f"**{t['component']}**")
        cols_header[1].markdown(f"**{t['pct_in_layer']}**")
        cols_header[2].markdown(f"**{t['density']}**")
        cols_header[3].markdown(f"**{t['cost_euro_kg']}**")
        
        layer_components = []
        
        # Valori predefiniti per simulare polimeri comuni (PE, PP, PA, EVOH, Tie)
        def_pcts = [100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        def_dens = [0.92, 0.90, 1.14, 1.17, 0.93, 0.92, 0.92]
        def_costs = [1.35, 1.40, 3.60, 8.80, 2.80, 1.35, 1.35]
        
        for comp_idx in range(1, 8):
            row_cols = st.columns([2, 2, 2, 2])
            with row_cols[0]:
                comp_name = st.text_input(f"Name C{comp_idx}", value=f"Material {comp_idx}" if comp_idx == 1 else "", key=f"name_{layer}_{comp_idx}")
            with row_cols[1]:
                comp_pct = row_cols[1].number_input(f"% C{comp_idx}", min_value=0.0, max_value=100.0, value=def_pcts[comp_idx-1], step=5.0, key=f"pct_{layer}_{comp_idx}")
            with row_cols[2]:
                comp_dens = row_cols[2].number_input(f"Density C{comp_idx}", min_value=0.0, value=def_dens[comp_idx-1], format="%.3f", key=f"dens_{layer}_{comp_idx}")
            with row_cols[3]:
                comp_cost = row_cols[3].number_input(f"Cost C{comp_idx}", min_value=0.0, value=def_costs[comp_idx-1], format="%.2f", key=f"cost_{layer}_{comp_idx}")
            
            if comp_pct > 0:
                layer_components.append({
                    "pct_in_layer": comp_pct,
                    "density": comp_dens,
                    "cost": comp_cost
                })
        
        # Controllo interno al singolo estrusore
        total_comp_pct = sum([c["pct_in_layer"] for c in layer_components])
        if abs(total_comp_pct - 100.0) > 0.01 and layer_splits[layer] > 0:
            st.warning(f"⚠️ {layer} components sum up to {total_comp_pct}%. It should be 100% if the layer is active.")
            
        recipe_data[layer] = layer_components

# --- 4. ENGINE DI CALCOLO COESTRUSIONE ---
# Calcolo densità media e costo medio per ogni singolo strato
layer_metrics = {}
for layer in layers:
    components = recipe_data[layer]
    if not components:
        layer_metrics[layer] = {"density": 0.0, "cost_per_kg": 0.0}
        continue
    
    total_pct = sum([c["pct_in_layer"] for c in components])
    
    # Media pesata delle proprietà dello strato
    if total_pct > 0:
        avg_density = sum([c["pct_in_layer"] * c["density"] for c in components]) / total_pct
        avg_cost_kg = sum([c["pct_in_layer"] * c["cost"] for c in components]) / total_pct
    else:
        avg_density, avg_cost_kg = 0.0, 0.0
        
    layer_metrics[layer] = {"density": avg_density, "cost_per_kg": avg_cost_kg}

# Calcolo delle proprietà globali del film (basate sulla ripartizione in volume/spessore % dei 9 strati)
total_film_density = sum([layer_splits[l] * layer_metrics[l]["density"] for l in layers]) / 100.0

# Calcolo del costo al kg finale basato sul peso effettivo di ciascuno strato nel film
# Peso strato_i = (Spessore % * Densità strato_i) / Densità globale film
total_material_cost_kg = 0.0
if total_film_density > 0:
    for l in layers:
        weight_fraction = (layer_splits[l] * layer_metrics[l]["density"]) / (total_film_density * 100.0)
        total_material_cost_kg += weight_fraction * layer_metrics[l]["cost_per_kg"]

# Indicatori Economici di Produzione
hourly_material_cost = hourly_output * total_material_cost_kg
annual_material_expenditure = hourly_material_cost * working_hours

# --- 5. VISUALIZZAZIONE RISULTATI E GRAFICI ---
st.markdown("---")
st.header(t["calc_results"])

m1, m2, m3, m4 = st.columns(4)
m1.metric(t["cost_kg_film"], f"€ {total_material_cost_kg:.3f}")
m2.metric(t["density_calc"], f"{total_film_density:.3f} g/cm³")
m3.metric(t["total_hourly_cost"], f"€ {hourly_material_cost:,.2f}")
m4.metric(t["annual_material_cost"], f"€ {annual_material_expenditure:,.0f}")

# Layout per Tabelle di Spessore e Grafici Struttura
c1, c2 = st.columns([2, 3])

with c1:
    st.subheader(t["layer_thick_table"])
    thickness_data = []
    for l in layers:
        thick_um = total_thickness * (layer_splits[l] / 100.0)
        weight_pct = ((layer_splits[l] * layer_metrics[l]["density"]) / total_film_density) if total_film_density > 0 else 0
        thickness_data.append({
            t["layer_name"]: l,
            "Thickness (µm)": f"{thick_um:.2f} µm",
            "Weight %": f"{weight_pct:.1f} %",
            "Cost (€/kg)": f"€ {layer_metrics[l]['cost_per_kg']:.2f}"
        })
    st.table(pd.DataFrame(thickness_data))

with c2:
    # Grafico a barre per mostrare l'impatto economico visivo della struttura simmetrica/asimmetrica
    st.subheader("Visual Layer Breakdown (Thickness vs Cost impact)")
    
    layer_thicknesses = [total_thickness * (layer_splits[l] / 100.0) for l in layers]
    layer_costs = [layer_metrics[l]["cost_per_kg"] for l in layers]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=layers,
        y=layer_thicknesses,
        text=[f"€{c:.2f}/kg" for c in layer_costs],
        textposition='auto',
        marker=dict(
            color=layer_costs, 
            colorscale='Viridis', 
            showscale=True,
            colorbar=dict(title="€/kg")
        )
    ))
    fig.update_layout(
        yaxis_title="Layer Thickness (µm)",
        xaxis_title="Film Structure (9 Layers)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
