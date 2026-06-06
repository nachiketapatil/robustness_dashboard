# import os
# import pandas as pd
# import plotly.graph_objects as go
# import streamlit as st

# # --- Page Configuration ---
# st.set_page_config(page_title="Robustness Evaluation Dashboard", layout="wide")

# # --- Constants & Mappings ---
# THRESH = 45

# COLORS = {
#     "CKA": "#1f77b4",
#     "HSIC": "#2ca02c",
#     "CKNNA": "#ff7f0e",
#     "SoftKNN": "#9467bd"
# }

# MARKERS = {
#     "CKA": "circle",
#     "HSIC": "square",
#     "CKNNA": "diamond",
#     "SoftKNN": "cross"
# }

# EVAL_METRICS = {
#     "MART": "mart_pgd",
#     "AutoAttack": "apgd-ce",
#     "ART": "art_pgd"
# }

# # --- Data Loading & Cleaning ---
# def clean_sheet(df):
#     df.columns = df.columns.str.strip()
#     df = df.dropna(how='all')
    
#     if "PGD Eval Steps" in df.columns:
#         df["PGD Eval Steps"] = df["PGD Eval Steps"].ffill()
        
#     if "clean" in df.columns:
#         df = df[df["clean"].notna()]
        
#     return df.reset_index(drop=True)

# @st.cache_data
# def load_data(dataset, epsilon):
#     """Loads and caches data based on dataset and epsilon selections."""
#     eps_str = epsilon.replace("/", "_")
#     file_name = f"Evals_{dataset.lower()}_{eps_str}.xlsx"
#     file_path = os.path.join("data", file_name)
    
#     if not os.path.exists(file_path):
#         return None, None, None
        
#     try:
#         pgd_raw = pd.read_excel(file_path, sheet_name="PGD")
#         trades_raw = pd.read_excel(file_path, sheet_name="TRADES")
#         methods_raw = pd.read_excel(file_path, sheet_name="Results")
        
#         pgd_df = clean_sheet(pgd_raw)
#         trades_df = clean_sheet(trades_raw)
#         methods_df = clean_sheet(methods_raw)
        
#         cols = ["clean", "mart_pgd", "apgd-ce", "art_pgd"]
        
#         for df in [pgd_df, trades_df, methods_df]:
#             for col in cols:
#                 if col in df.columns:
#                     df[col] = pd.to_numeric(df[col], errors='coerce')
                    
#         return pgd_df, trades_df, methods_df
#     except Exception as e:
#         st.error(f"Error loading {file_name}: {e}")
#         return None, None, None

# # --- Plotting Function ---
# def make_plot(pgd_df, trades_df, methods_df, eval_steps, eval_col, title):
#     fig = go.Figure()

#     # ===== PGD =====
#     df = pgd_df[pgd_df["PGD Eval Steps"] == eval_steps]
#     df = df[(df["clean"] >= THRESH) & (df[eval_col] >= THRESH)]

#     fig.add_trace(go.Scatter(
#         x=df["clean"], y=df[eval_col], mode='markers',
#         marker=dict(color="red", size=12, symbol="circle" if eval_steps == 10 else "triangle-up"),
#         name=f"PGD-{eval_steps}",
#         text=[f"PGD<br>Train={tr}<br>Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
#               for tr, ts, c, r in zip(df["Training"], df["PGD Steps"], df["clean"], df[eval_col])],
#         hoverinfo="text"
#     ))

#     # ===== TRADES =====
#     df = trades_df[trades_df["PGD Eval Steps"] == eval_steps]
#     df = df[(df["clean"] >= THRESH) & (df[eval_col] >= THRESH)]

#     fig.add_trace(go.Scatter(
#         x=df["clean"], y=df[eval_col], mode='markers',
#         marker=dict(color="black", size=12, symbol="diamond" if eval_steps == 10 else "diamond-open"),
#         name=f"TRADES-{eval_steps}",
#         text=[f"TRADES<br>β={b}<br>Train={tr}<br>Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
#               for b, tr, ts, c, r in zip(df["beta"], df["Training"], df["PGD Steps"], df["clean"], df[eval_col])],
#         hoverinfo="text"
#     ))

#     # ===== METHODS (Representation Alignment) =====
#     df = methods_df[methods_df["PGD Eval Steps"] == eval_steps]
#     df = df[(df["clean"] >= THRESH) & (df[eval_col] >= THRESH)]

#     for method in df["Method"].dropna().unique():
#         sub = df[df["Method"] == method]
#         fig.add_trace(go.Scatter(
#             x=sub["clean"], y=sub[eval_col], mode='markers',
#             marker=dict(
#                 color=COLORS.get(method, "gray"),
#                 symbol=MARKERS.get(method, "circle"),
#                 size=11
#             ),
#             name=method,
#             text=[f"{method}<br>λ={lam}<br>Train Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
#                   for lam, ts, c, r in zip(sub["λ"], sub["PGD Steps"], sub["clean"], sub[eval_col])],
#             hoverinfo="text"
#         ))

#     fig.update_layout(
#         title=f"{title} (Eval Steps = {eval_steps})",
#         xaxis_title="Clean Accuracy (%)",
#         yaxis_title="Robust Accuracy (%)",
#         template="plotly_white",
#         height=550,
#         legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
#     )
#     return fig


# # --- Main UI ---
# st.title("🛡️ Model Robustness Evaluation Dashboard")
# st.markdown("Compare PGD-AT, TRADES, and representation alignment methods across threat models.")

# # Sidebar Controls
# with st.sidebar:
#     st.header("Experiment Parameters")
#     selected_dataset = st.selectbox("Dataset", ["CIFAR10", "Imagenette", "SVHN"])
#     selected_epsilon = st.selectbox("Epsilon (Perturbation Bound)", ["4/255", "8/255", "12/255", "20/255"])
#     selected_eval_steps = st.radio("PGD Evaluation Steps", [10, 20])

# # Load Data based on selection
# pgd_df, trades_df, methods_df = load_data(selected_dataset, selected_epsilon)

# if pgd_df is None:
#     st.warning(f"Data file not found for **{selected_dataset}** at epsilon **{selected_epsilon}**.")
#     st.info("Expected file: `data/Evals_" + selected_dataset.lower() + "_" + selected_epsilon.replace("/", "_") + ".xlsx`")
# else:
#     # Render Plots in Tabs for cleaner viewing
#     st.subheader(f"Results for {selected_dataset} (ε = {selected_epsilon})")
    
#     tab1, tab2, tab3 = st.tabs(["MART Evaluation", "AutoAttack (APGD-CE)", "ART Evaluation"])
    
#     with tab1:
#         fig_mart = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "mart_pgd", "MART")
#         st.plotly_chart(fig_mart, use_container_width=True)
        
#     with tab2:
#         fig_aa = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "apgd-ce", "AutoAttack")
#         st.plotly_chart(fig_aa, use_container_width=True)
        
#     with tab3:
#         fig_art = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "art_pgd", "ART")
#         st.plotly_chart(fig_art, use_container_width=True)

#     # Optional: Display Raw Data Checkbox
#     if st.checkbox("Show Raw DataFrame Summaries"):
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.write("PGD Baselines", pgd_df)
#         with col2:
#             st.write("TRADES", trades_df)
#         with col3:
#             st.write("Methods (CKA, CKNNA, HSIC...)", methods_df)

import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Robustness Evaluation Dashboard", layout="wide")

# --- Constants & Mappings ---
COLORS = {
    "CKA": "#1f77b4",
    "HSIC": "#2ca02c",
    "CKNNA": "#ff7f0e",
    "SoftKNN": "#9467bd"
}

MARKERS = {
    "CKA": "circle",
    "HSIC": "square",
    "CKNNA": "diamond",
    "SoftKNN": "cross"
}

# --- Data Loading & Cleaning ---
def clean_sheet(df):
    df.columns = df.columns.str.strip()
    df = df.dropna(how='all')
    
    if "PGD Eval Steps" in df.columns:
        df["PGD Eval Steps"] = df["PGD Eval Steps"].ffill()
        
    if "clean" in df.columns:
        df = df[df["clean"].notna()]
        
    return df.reset_index(drop=True)

@st.cache_data
def load_data(dataset, epsilon):
    """Loads and caches data based on dataset and epsilon selections."""
    eps_str = epsilon.replace("/", "_")
    file_name = f"Evals_{dataset.lower()}_{eps_str}.xlsx"
    file_path = os.path.join("data", file_name)
    
    if not os.path.exists(file_path):
        return None, None, None
        
    try:
        pgd_raw = pd.read_excel(file_path, sheet_name="PGD")
        trades_raw = pd.read_excel(file_path, sheet_name="TRADES")
        methods_raw = pd.read_excel(file_path, sheet_name="Results")
        
        pgd_df = clean_sheet(pgd_raw)
        trades_df = clean_sheet(trades_raw)
        methods_df = clean_sheet(methods_raw)
        
        cols = ["clean", "mart_pgd", "apgd-ce", "art_pgd"]
        
        for df in [pgd_df, trades_df, methods_df]:
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        return pgd_df, trades_df, methods_df
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return None, None, None

# --- Plotting Function ---
def make_plot(pgd_df, trades_df, methods_df, eval_steps, eval_col, title, accuracy_thresh):
    fig = go.Figure()

    # ===== PGD =====
    df = pgd_df[pgd_df["PGD Eval Steps"] == eval_steps]
    df = df[(df["clean"] >= accuracy_thresh) & (df[eval_col] >= accuracy_thresh)]

    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df["clean"], y=df[eval_col], mode='markers',
            marker=dict(color="red", size=12, symbol="circle" if eval_steps == 10 else "triangle-up"),
            name=f"PGD-{eval_steps}",
            text=[f"PGD<br>Train={tr}<br>Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
                  for tr, ts, c, r in zip(df["Training"], df["PGD Steps"], df["clean"], df[eval_col])],
            hoverinfo="text"
        ))

    # ===== TRADES =====
    df = trades_df[trades_df["PGD Eval Steps"] == eval_steps]
    df = df[(df["clean"] >= accuracy_thresh) & (df[eval_col] >= accuracy_thresh)]

    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df["clean"], y=df[eval_col], mode='markers',
            marker=dict(color="black", size=12, symbol="diamond" if eval_steps == 10 else "diamond-open"),
            name=f"TRADES-{eval_steps}",
            text=[f"TRADES<br>β={b}<br>Train={tr}<br>Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
                  for b, tr, ts, c, r in zip(df["beta"], df["Training"], df["PGD Steps"], df["clean"], df[eval_col])],
            hoverinfo="text"
        ))

    # ===== METHODS =====
    df = methods_df[methods_df["PGD Eval Steps"] == eval_steps]
    df = df[(df["clean"] >= accuracy_thresh) & (df[eval_col] >= accuracy_thresh)]

    if not df.empty:
        for method in df["Method"].dropna().unique():
            sub = df[df["Method"] == method]
            fig.add_trace(go.Scatter(
                x=sub["clean"], y=sub[eval_col], mode='markers',
                marker=dict(
                    color=COLORS.get(method, "gray"),
                    symbol=MARKERS.get(method, "circle"),
                    size=11
                ),
                name=method,
                text=[f"{method}<br>λ={lam}<br>Train Steps={ts}<br>Clean={c:.2f}<br>{eval_col}={r:.2f}"
                      for lam, ts, c, r in zip(sub["λ"], sub["PGD Steps"], sub["clean"], sub[eval_col])],
                hoverinfo="text"
            ))

    fig.update_layout(
        title=f"{title} (Eval Steps = {eval_steps})",
        xaxis_title="Clean Accuracy (%)",
        yaxis_title="Robust Accuracy (%)",
        template="plotly_white",
        height=550,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    return fig


# --- Main UI ---
st.title("🛡️ Model Robustness Evaluation Dashboard")
st.markdown("Compare PGD-AT, TRADES, and representation alignment methods across threat models.")

# Sidebar Controls
with st.sidebar:
    st.header("Experiment Parameters")
    selected_dataset = st.selectbox("Dataset", ["CIFAR10", "Imagenette", "SVHN"])
    selected_epsilon = st.selectbox("Epsilon (Perturbation Bound)", ["4/255", "8/255", "12/255", "20/255"])
    selected_eval_steps = st.radio("PGD Evaluation Steps", [10, 20])
    
    # Dynamic threshold slider to prevent high-epsilon filtering bugs
    thresh_slider = st.slider("Minimum Accuracy Filter (%)", min_value=0, max_value=100, value=0)

# Load Data based on selection
pgd_df, trades_df, methods_df = load_data(selected_dataset, selected_epsilon)

if pgd_df is None:
    st.warning(f"Data file not found for **{selected_dataset}** at epsilon **{selected_epsilon}**.")
    st.info(f"Expected path: `data/Evals_{selected_dataset.lower()}_{selected_epsilon.replace('/', '_')}.xlsx`")
else:
    st.subheader(f"Results for {selected_dataset} (ε = {selected_epsilon})")
    
    tab1, tab2, tab3 = st.tabs(["MART Evaluation", "AutoAttack (APGD-CE)", "ART Evaluation"])
    
    with tab1:
        fig_mart = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "mart_pgd", "MART", thresh_slider)
        st.plotly_chart(fig_mart, use_container_width=True)
        
    with tab2:
        fig_aa = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "apgd-ce", "AutoAttack", thresh_slider)
        st.plotly_chart(fig_aa, use_container_width=True)
        
    with tab3:
        fig_art = make_plot(pgd_df, trades_df, methods_df, selected_eval_steps, "art_pgd", "ART", thresh_slider)
        st.plotly_chart(fig_art, use_container_width=True)

    if st.checkbox("Show Raw Data Split Previews"):
        col1, col2, col3 = st.columns(3)
        col1.write("**PGD Sheet**", pgd_df)
        col2.write("**TRADES Sheet**", trades_df)
        col3.write("**Results Sheet**", methods_df)
