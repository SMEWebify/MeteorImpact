import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output

# --- 1. CHARGEMENT ---
df_raw = pd.read_csv('sample_data/meteorite-landings.csv', sep=';')
mapping = {
    'Name / Nom': 'name',
    'Year / Année': 'year_num',
    'Country / Pays': 'country',
    'Class / Classe': 'class',
    'Mass (g) / Masse (g)': 'mass_g',
    'Latitude': 'lat',
    'Longitude': 'lon'
}
df_raw = df_raw.rename(columns=mapping)
df_raw = df_raw.dropna(subset=['year_num', 'mass_g', 'country'])
df_raw['year_num'] = df_raw['year_num'].astype(int)

# --- 2. FONCTION DE VISUALISATION ---
def create_dashboard(mass_min, year_range, top_n):
    # Filtrage
    mask = (
        (df_raw['mass_g'] >= mass_min) &
        (df_raw['year_num'] >= year_range[0]) &
        (df_raw['year_num'] <= year_range[1])
    )
    df = df_raw[mask].copy()

    if df.empty:
        print("Aucune donnée pour ces filtres.")
        return

    # A. Top Pays (Bar Chart)
    top_df = df['country'].value_counts().head(top_n).reset_index()
    fig_bar = px.bar(top_df, x='count', y='country', orientation='h',
                     title=f"Top {top_n} des pays", color='count',
                     template="plotly_dark", labels={'count':'Nombre', 'country':'Pays'})
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)

    # B. Évolution temporelle (Line Chart)
    year_counts = df.groupby('year_num').size().reset_index(name='counts')
    fig_line = px.line(year_counts, x='year_num', y='counts',
                       title="Évolution des découvertes",
                       template="plotly_dark")
    fig_line.update_traces(line_color='#00CC96')

    # C. Répartition des masses (Histogramme Log)
    fig_hist = px.histogram(df, x="mass_g", log_x=True,
                            title="Distribution des masses (échelle Log)",
                            template="plotly_dark", color_discrete_sequence=['#AB63FA'])
    fig_hist.update_layout(xaxis_title="Masse (g)", yaxis_title="Fréquence")

    # Affichage
    display(fig_bar)
    display(fig_line)
    display(fig_hist)

# --- 3. INTERFACE ---
style = {'description_width': 'initial'}
mass_slider = widgets.FloatLogSlider(value=1000, base=10, min=0, max=7, step=0.1, description="Masse min (g)", style=style)
year_slider = widgets.IntRangeSlider(value=[1850, 2025], min=1400, max=2025, description="Période", style=style)
top_slider = widgets.IntSlider(value=10, min=5, max=30, description="Nb Pays", style=style)

out = widgets.Output()

def on_value_change(change):
    with out:
        clear_output(wait=True)
        create_dashboard(mass_slider.value, year_slider.value, top_slider.value)

# Lier les widgets
mass_slider.observe(on_value_change, names='value')
year_slider.observe(on_value_change, names='value')
top_slider.observe(on_value_change, names='value')

# Mise en page
ui = widgets.VBox([
    widgets.HTML("<h2>📊 Analyse Statistique des Météorites</h2>"),
    widgets.HBox([mass_slider, year_slider, top_slider])
])

display(ui, out)
on_value_change(None) # Premier affichage