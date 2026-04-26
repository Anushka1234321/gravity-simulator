import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Universe Gravity Simulator", page_icon="🌌", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; background-color: #00000f; color: #e0e8ff; }
.stApp { background: radial-gradient(ellipse at center, #0a0a2e 0%, #00000f 70%); }
h1, h2, h3 { font-family: 'Orbitron', monospace !important; color: #7eb8ff !important; letter-spacing: 2px; }
.info-card { background: rgba(10,20,60,0.8); border: 1px solid rgba(100,160,255,0.3); border-radius: 12px; padding: 16px; margin: 8px 0; }
.stSlider label { color: #7eb8ff !important; font-family: 'Orbitron', monospace !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🌌 UNIVERSE GRAVITY SIMULATOR")
st.markdown("<p style='color:rgba(126,184,255,0.6);font-family:Orbitron;font-size:11px;letter-spacing:3px;'>REAL NEWTONIAN GRAVITY PHYSICS</p>", unsafe_allow_html=True)

# Object types
OBJECT_TYPES = {
    "⭐ Star":        {"mass": 1000,   "color": "#FDB813", "size": 14, "trail_color": "rgba(253,184,19,0.3)"},
    "🪐 Planet":      {"mass": 10,     "color": "#4fa3e0", "size": 8,  "trail_color": "rgba(79,163,224,0.3)"},
    "⚫ Black Hole":  {"mass": 50000,  "color": "#9b30ff", "size": 20, "trail_color": "rgba(155,48,255,0.3)"},
    "💫 Neutron Star":{"mass": 8000,   "color": "#00ffff", "size": 10, "trail_color": "rgba(0,255,255,0.3)"},
    "🌠 Asteroid":    {"mass": 1,      "color": "#a0a0a0", "size": 5,  "trail_color": "rgba(160,160,160,0.2)"},
}

G = 0.1  # Gravitational constant (scaled)
BOUNDARY = 50

def compute_gravity(objects, dt, speed):
    if len(objects) == 0:
        return objects

    positions = np.array([[o["x"], o["y"]] for o in objects], dtype=float)
    velocities = np.array([[o["vx"], o["vy"]] for o in objects], dtype=float)
    masses = np.array([o["mass"] for o in objects], dtype=float)
    to_remove = set()

    for i in range(len(objects)):
        fx, fy = 0.0, 0.0
        for j in range(len(objects)):
            if i == j:
                continue
            dx = positions[j][0] - positions[i][0]
            dy = positions[j][1] - positions[i][1]
            dist = max(np.sqrt(dx**2 + dy**2), 1.0)

            # Black hole swallows nearby objects
            if objects[j]["type"] == "⚫ Black Hole" and dist < 3:
                to_remove.add(i)
                continue

            # Collision
            if dist < 2 and i not in to_remove and j not in to_remove:
                if masses[i] < masses[j]:
                    to_remove.add(i)
                continue

            force = G * masses[i] * masses[j] / (dist ** 2)
            fx += force * dx / dist
            fy += force * dy / dist

        if i not in to_remove:
            velocities[i][0] += (fx / masses[i]) * dt * speed
            velocities[i][1] += (fy / masses[i]) * dt * speed

    new_objects = []
    for i, o in enumerate(objects):
        if i in to_remove:
            continue
        o = o.copy()
        o["vx"] = velocities[i][0]
        o["vy"] = velocities[i][1]
        o["x"] += o["vx"] * dt * speed
        o["y"] += o["vy"] * dt * speed

        # Bounce off boundaries
        if abs(o["x"]) > BOUNDARY:
            o["vx"] *= -0.8
            o["x"] = np.clip(o["x"], -BOUNDARY, BOUNDARY)
        if abs(o["y"]) > BOUNDARY:
            o["vy"] *= -0.8
            o["y"] = np.clip(o["y"], -BOUNDARY, BOUNDARY)

        # Update trail
        trail = o.get("trail", [])
        trail.append((o["x"], o["y"]))
        if len(trail) > 40:
            trail = trail[-40:]
        o["trail"] = trail

        new_objects.append(o)

    return new_objects

# Init session state
if "objects" not in st.session_state:
    st.session_state.objects = []
if "running" not in st.session_state:
    st.session_state.running = False
if "steps" not in st.session_state:
    st.session_state.steps = 0

col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("### ⚙️ ADD OBJECT")
    obj_type = st.selectbox("Type", list(OBJECT_TYPES.keys()))
    x_pos = st.slider("X Position", -45, 45, 0)
    y_pos = st.slider("Y Position", -45, 45, 0)
    vx = st.slider("X Velocity", -10, 10, 2)
    vy = st.slider("Y Velocity", -10, 10, 0)

    if st.button("➕ Add Object", use_container_width=True):
        data = OBJECT_TYPES[obj_type]
        st.session_state.objects.append({
            "type": obj_type,
            "x": float(x_pos),
            "y": float(y_pos),
            "vx": float(vx),
            "vy": float(vy),
            "mass": data["mass"],
            "color": data["color"],
            "size": data["size"],
            "trail_color": data["trail_color"],
            "trail": []
        })

    st.markdown("### 🎮 SIMULATION")
    sim_speed = st.slider("Speed", 1, 10, 3)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Step", use_container_width=True):
            st.session_state.objects = compute_gravity(st.session_state.objects, 0.1, sim_speed)
            st.session_state.steps += 1
    with c2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.objects = []
            st.session_state.steps = 0

    # Presets
    st.markdown("### 🌠 PRESETS")
    if st.button("🌍 Solar System", use_container_width=True):
        st.session_state.objects = [
            {"type": "⭐ Star", "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "mass": 10000, "color": "#FDB813", "size": 18, "trail_color": "rgba(253,184,19,0.3)", "trail": []},
            {"type": "🪐 Planet", "x": 10.0, "y": 0.0, "vx": 0.0, "vy": 10.0, "mass": 10, "color": "#4fa3e0", "size": 8, "trail_color": "rgba(79,163,224,0.3)", "trail": []},
            {"type": "🪐 Planet", "x": 20.0, "y": 0.0, "vx": 0.0, "vy": 7.0, "mass": 20, "color": "#c1440e", "size": 10, "trail_color": "rgba(193,68,14,0.3)", "trail": []},
            {"type": "🪐 Planet", "x": 35.0, "y": 0.0, "vx": 0.0, "vy": 5.0, "mass": 50, "color": "#c88b3a", "size": 13, "trail_color": "rgba(200,139,58,0.3)", "trail": []},
        ]
        st.session_state.steps = 0

    if st.button("⚫ Black Hole", use_container_width=True):
        st.session_state.objects = [
            {"type": "⚫ Black Hole", "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "mass": 50000, "color": "#9b30ff", "size": 22, "trail_color": "rgba(155,48,255,0.3)", "trail": []},
            {"type": "⭐ Star", "x": 20.0, "y": 0.0, "vx": 0.0, "vy": 15.0, "mass": 1000, "color": "#FDB813", "size": 14, "trail_color": "rgba(253,184,19,0.3)", "trail": []},
            {"type": "⭐ Star", "x": -20.0, "y": 0.0, "vx": 0.0, "vy": -15.0, "mass": 1000, "color": "#FDB813", "size": 14, "trail_color": "rgba(253,184,19,0.3)", "trail": []},
            {"type": "🌠 Asteroid", "x": 30.0, "y": 10.0, "vx": -5.0, "vy": 8.0, "mass": 1, "color": "#a0a0a0", "size": 5, "trail_color": "rgba(160,160,160,0.2)", "trail": []},
            {"type": "🌠 Asteroid", "x": -30.0, "y": -10.0, "vx": 5.0, "vy": -8.0, "mass": 1, "color": "#a0a0a0", "size": 5, "trail_color": "rgba(160,160,160,0.2)", "trail": []},
        ]
        st.session_state.steps = 0

    if st.button("💫 Binary Stars", use_container_width=True):
        st.session_state.objects = [
            {"type": "⭐ Star", "x": -15.0, "y": 0.0, "vx": 0.0, "vy": -8.0, "mass": 5000, "color": "#FDB813", "size": 16, "trail_color": "rgba(253,184,19,0.3)", "trail": []},
            {"type": "⭐ Star", "x": 15.0, "y": 0.0, "vx": 0.0, "vy": 8.0, "mass": 5000, "color": "#ff6b6b", "size": 16, "trail_color": "rgba(255,107,107,0.3)", "trail": []},
            {"type": "🪐 Planet", "x": 0.0, "y": 30.0, "vx": 12.0, "vy": 0.0, "mass": 10, "color": "#4fa3e0", "size": 8, "trail_color": "rgba(79,163,224,0.3)", "trail": []},
        ]
        st.session_state.steps = 0

    st.markdown(f"""
    <div class="info-card">
        <p style="margin:2px;font-size:12px;">🔢 Objects: {len(st.session_state.objects)}</p>
        <p style="margin:2px;font-size:12px;">⏱️ Steps: {st.session_state.steps}</p>
    </div>
    """, unsafe_allow_html=True)

with col1:
    fig = go.Figure()

    # Stars background
    np.random.seed(99)
    bx = np.random.uniform(-50, 50, 300)
    by = np.random.uniform(-50, 50, 300)
    fig.add_trace(go.Scatter(
        x=bx, y=by, mode='markers',
        marker=dict(size=1, color='white', opacity=0.5),
        hoverinfo='skip', showlegend=False
    ))

    # Draw trails and objects
    for o in st.session_state.objects:
        trail = o.get("trail", [])
        if len(trail) > 1:
            tx = [t[0] for t in trail]
            ty = [t[1] for t in trail]
            fig.add_trace(go.Scatter(
                x=tx, y=ty, mode='lines',
                line=dict(color=o["trail_color"], width=2),
                hoverinfo='skip', showlegend=False
            ))

        # Glow effect for black hole
        if o["type"] == "⚫ Black Hole":
            for r, op in [(40, 0.05), (30, 0.1), (20, 0.15)]:
                fig.add_shape(type="circle",
                    xref="x", yref="y",
                    x0=o["x"]-r*0.3, y0=o["y"]-r*0.3,
                    x1=o["x"]+r*0.3, y1=o["y"]+r*0.3,
                    fillcolor=f"rgba(155,48,255,{op})",
                    line=dict(color="rgba(155,48,255,0.1)", width=0)
                )

        fig.add_trace(go.Scatter(
            x=[o["x"]], y=[o["y"]],
            mode='markers+text',
            marker=dict(
                size=o["size"],
                color=o["color"],
                line=dict(color='white', width=1),
                symbol='circle'
            ),
            text=[o["type"].split()[0]],
            textposition='top center',
            textfont=dict(color=o["color"], size=12),
            name=o["type"],
            hovertemplate=f'<b>{o["type"]}</b><br>Mass: {o["mass"]}<br>Vel: ({o["vx"]:.1f}, {o["vy"]:.1f})<extra></extra>'
        ))

    fig.update_layout(
        paper_bgcolor='#00000f',
        plot_bgcolor='#00000f',
        xaxis=dict(range=[-52, 52], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-52, 52], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div style='text-align:center;color:rgba(126,184,255,0.4);font-family:Orbitron;font-size:10px;letter-spacing:2px;margin-top:8px;'>
    ADD OBJECTS → CLICK STEP TO SIMULATE → WATCH GRAVITY IN ACTION
</div>
""", unsafe_allow_html=True)
