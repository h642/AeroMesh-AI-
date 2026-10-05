import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Initialize high-res figure matching the 16:9 / clean slide aspect ratio
fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8.5)
ax.axis('off')

# Style parameters matching the reference style
outer_box_style = dict(boxstyle="round,pad=0.2,rounding_size=0.15", ec="black", fc="white", lw=2.2)
inner_box_style = dict(boxstyle="round,pad=0.3,rounding_size=0.12", ec="black", fc="white", lw=1.8)
arrow_props = dict(arrowstyle="->", color="black", lw=1.8, mutation_scale=14)

def draw_labeled_box(x, y, w, h, title, parent=True):
    style = outer_box_style if parent else inner_box_style
    rect = patches.FancyBboxPatch((x, y), w, h, **style)
    ax.add_patch(rect)
    
    if parent:
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", 
                fontsize=13, fontweight="bold", fontfamily="sans-serif")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", 
                fontsize=10.5, fontweight="bold", fontfamily="sans-serif", multialignment='center')

# ==========================================
# 1. TOP-LEFT: DATA INGESTION (Analogous to "Sensor")
# ==========================================
draw_labeled_box(0.4, 2.6, 2.8, 5.5, "Data Ingestion", parent=True)

# Inner Box 1: Raw NWP Data
draw_labeled_box(0.6, 6.4, 2.4, 1.1, "NCUM & NEPS-G\n4D Ensemble (12km)", parent=False)

# Inner Box 2: Pre-processing & Chunking
draw_labeled_box(0.6, 4.6, 2.4, 1.1, "xarray + Dask\nLazy Chunk Engine", parent=False)

# Inner Box 3: Climatology Engine
draw_labeled_box(0.6, 2.8, 2.4, 1.1, "ERA5 30-Year\nClimatology Baseline", parent=False)

# Internal Arrows (Data Ingestion)
ax.annotate("", xy=(1.8, 5.7), xytext=(1.8, 6.4), arrowprops=arrow_props)
ax.text(1.8, 6.05, "NetCDF / GRIB2", ha="center", va="center", fontsize=8, backgroundcolor="white")

ax.annotate("", xy=(1.8, 3.9), xytext=(1.8, 4.6), arrowprops=arrow_props)
ax.text(1.8, 4.25, "EFI Anomaly Stream", ha="center", va="center", fontsize=8, backgroundcolor="white")


# ==========================================
# 2. TOP-MIDDLE: BACKEND
# ==========================================
draw_labeled_box(3.5, 2.6, 3.8, 5.5, "Backend", parent=True)

# Inner Box 1: Spatial DB
draw_labeled_box(4.2, 6.4, 2.4, 1.1, "PostGIS / SQLite\nSpatial Database", parent=False)

# Inner Box 2: Core Server
draw_labeled_box(3.9, 4.2, 3.0, 1.5, "FastAPI Backend\nOperational Server", parent=False)

# Internal Arrows (Backend)
ax.annotate("", xy=(5.4, 6.4), xytext=(5.4, 5.7), arrowprops=arrow_props)
ax.text(5.4, 6.05, "Stores Assets & Tracks", ha="center", va="center", fontsize=8, backgroundcolor="white")


# ==========================================
# 3. TOP-RIGHT: FRONTEND
# ==========================================
draw_labeled_box(7.6, 2.6, 3.0, 5.5, "Frontend", parent=True)

# Inner Box 1: Web Dashboard
draw_labeled_box(7.9, 6.4, 2.4, 1.1, "Interactive Leaflet\nMission Dashboard", parent=False)

# Inner Box 2: First Responder UI
draw_labeled_box(7.9, 4.6, 2.4, 1.1, "NDRF Incident\nCommander View", parent=False)

# Inner Box 3: Alert Dispatching
draw_labeled_box(7.9, 2.8, 2.4, 1.1, "CAP XML /\nSMS / PDF Alerts", parent=False)

# Internal Arrows (Frontend)
ax.annotate("", xy=(9.1, 5.7), xytext=(9.1, 6.4), arrowprops=arrow_props)
ax.annotate("", xy=(9.1, 4.6), xytext=(9.1, 3.9), arrowprops=arrow_props)


# ==========================================
# 4. BOTTOM: ALGORITHM (Spans full width)
# ==========================================
draw_labeled_box(0.4, 0.3, 10.2, 2.0, "Algorithm", parent=True)

# Sub-Algorithm 1: Stage 1 GNN
draw_labeled_box(0.8, 0.55, 4.2, 1.1, "Stage 1: Spherical Mesh GNN\n(Trajectory & 4D Bounding Box)", parent=False)

# Sub-Algorithm 2: Stage 2 Diffusion
draw_labeled_box(5.8, 0.55, 4.4, 1.1, "Stage 2: Physics-Guided Diffusion\n(5km Amplitude Preserved Downscaling)", parent=False)

# Algorithm Internal Arrow
ax.annotate("", xy=(5.8, 1.1), xytext=(5.0, 1.1), arrowprops=arrow_props)
ax.text(5.4, 1.25, "Cropped Macro-Slice", ha="center", va="center", fontsize=8, backgroundcolor="white")


# ==========================================
# 5. CROSS-MODULE ROUTING ARROWS (Matching exact flow)
# ==========================================

# Data Ingestion -> Backend (Curved line from LoRa/Clim position)
ax.annotate("", xy=(4.2, 4.6), xytext=(3.0, 3.35),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.8, 
                            connectionstyle="arc3,rad=-0.25", mutation_scale=14))
ax.text(3.7, 4.0, "Sends 4D Grid\nPayload", ha="center", va="center", fontsize=8, backgroundcolor="white")

# Backend <-> Algorithm (Bi-directional communication)
ax.annotate("", xy=(5.4, 2.3), xytext=(5.4, 4.2), arrowprops=arrow_props)
ax.annotate("", xy=(5.4, 4.2), xytext=(5.4, 2.3), arrowprops=arrow_props)
ax.text(5.4, 3.25, "Requests Inference &\nReturns 5km Grid", ha="center", va="center", fontsize=8, backgroundcolor="white")

# Backend -> Frontend Alerts (Curved line to SMS / Alerts)
ax.annotate("", xy=(7.9, 3.35), xytext=(6.9, 4.6),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.8,
                            connectionstyle="arc3,rad=-0.2", mutation_scale=14))
ax.text(7.35, 4.05, "Pushes 5km Alerts\n& Directives", ha="center", va="center", fontsize=8, backgroundcolor="white")

plt.tight_layout()
plt.savefig("aeromesh_architecture_diagram.png", dpi=300, bbox_inches='tight')
print("✅ Diagram saved successfully as 'aeromesh_architecture_diagram.png'!")