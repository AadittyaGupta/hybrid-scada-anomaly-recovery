
from altair import value
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.preprocessing import preprocess_data
from services.anomaly_detection import train_isolation_forest, detect_anomalies
from services.pattern_detection import detect_patterns
from services.risk_analysis import classify_risk
from services.simulation import stream_data, inject_attack
from services.response import apply_response
from services.explain import explain_anomaly
from Utils.logger import log_event      
from services.data_loader import load_full_dataset

# df = load_full_dataset()             

if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False

# ---------------------------
# RISK SCORE FUNCTION 
# ---------------------------
def calculate_risk_score(df, patterns):         
    
    anomaly_ratio = df['final_anomaly'].mean()  # % anomalies

    anomaly_score = anomaly_ratio * 70
    pattern_score = len(patterns) * 15

    score = anomaly_score + pattern_score

    return min(score, 100)

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="SCADA Cyber Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }

    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }

    h1, h2, h3 {
        color: #00BFFF;
    }

    .stDataFrame {
        background-color: #1c1f26;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("⚡ SCADA Monitor")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home","⚡ Live SCADA Simulation", "📊 Dashboard", "🚨 Alerts", "📋 Report"]
)


uploaded_files = st.sidebar.file_uploader(
    "Upload SCADA CSV(s)",
    type=["csv"],
    accept_multiple_files=True
)

# ---------------------------
# LIVE SIMULATION CONTROLS 
# ---------------------------
# simulate = st.sidebar.checkbox("Enable Live Simulation")

# ----- BUTTON TO START SIMULATION ------

if "start_sim" not in st.session_state:
    st.session_state.start_sim = False

if st.sidebar.button("▶️ Start Simulation"):
    st.session_state.start_sim = True
    st.session_state.logs = []   # reset logs

if "logs" not in st.session_state:
    st.session_state.logs = []

speed = st.sidebar.slider("Simulation Speed", 0.1, 1.0, 0.3)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("<h1 style='text-align:center;'>⚡ SCADA Cyber Threat Detection System</h1>", unsafe_allow_html=True)

# ---------------------------
# HOME 
# ---------------------------
if page == "🏠 Home":

    st.markdown("## What is SCADA?")

    st.markdown("""
    SCADA (Supervisory Control and Data Acquisition) is a system used to **monitor, control, and manage industrial processes** such as power grids, water supply systems, and manufacturing plants.

    A typical SCADA system consists of:

    - **Control Center (HMI)** – Where operators monitor the system  
    - **Sensors & Devices** – Collect real-time data (voltage, current, etc.)  
    - **RTUs/PLCs** – Process data and execute control commands  
    - **Communication Network** – Connects all components together  

    These systems continuously collect data from the field and allow operators to make decisions or take actions remotely.

    ---

    ### Why SCADA is Important

    SCADA systems are critical because they ensure:

    - Reliable power distribution  
    - Continuous water supply  
    - Safe industrial operations  

    Any disruption in these systems can directly impact daily life and infrastructure.
    """)

    st.markdown("---")

    # ---------------------------
    # CYBER SECURITY IMPORTANCE
    # ---------------------------
    st.markdown("## Cybersecurity in SCADA Systems")

    st.markdown("""
    Modern SCADA systems are increasingly connected to networks, making them more efficient—but also more vulnerable to cyber threats.

    As critical infrastructure becomes digital, cyber attacks can lead to:
    
    -  Power outages and grid instability  
    -  Economic and operational losses  
    -  Safety risks for people and equipment  

    Because of this, monitoring system behavior and detecting unusual activity has become extremely important.
    """)

    st.info(" Even small anomalies in system data can indicate larger underlying issues or potential cyber threats.")

    st.markdown("---")
        
    st.markdown("###  Key Features")

    col1, col2, col3 = st.columns(3)

    col1.info("""
    **📊 Real-time Monitoring**
    
    Analyze voltage, current, and frequency trends with anomaly highlighting.
    """)

    col2.info("""
    **🚨 Intelligent Alerts**
    
    Detect coordinated attacks, spikes, and sensor tampering patterns.
    """)

    col3.info("""
    **📈 Risk Assessment**
    
    Classifies system risk into LOW / MEDIUM / HIGH levels.
              

    """)


    st.markdown("## SCADA Cyber Attack Types")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander(" False Data Injection"):
            st.write("Attackers manipulate sensor values to mislead operators.")

        with st.expander(" Denial of Service (DoS)"):
            st.write("System is overloaded, preventing normal operation.")

    with col2:
        with st.expander("Replay Attack"):
            st.write("Old valid data is resent to hide real conditions.")

        with st.expander(" Command Injection"):
            st.write("Unauthorized commands sent to control systems.")

    # col1, col2, col3 = st.columns(3)

    # col1.info("📊 Real-time monitoring of SCADA signals")
    # col2.info("🚨 Intelligent cyber threat alerts")
    # col3.info("📈 Automated risk classification")


        # Key Features
    

    st.markdown("---")

    st.markdown("### 🔄 Workflow")
    st.markdown("""
    1️⃣ Upload dataset  
    2️⃣ Preprocess data  
    3️⃣ Detect anomalies  
    4️⃣ Identify attack patterns  
    5️⃣ Classify risk  
    """)

    # st.markdown("---")

    # st.markdown("### 🛠️ Tech Stack")
    # st.code("Python | Streamlit | Scikit-learn | Pandas | Plotly")

    st.success("⬅️ Upload dataset from sidebar to begin")



# ---------------------------
# LIVE SCADA SIMULAION (ONE MONTH DATA)
# ---------------------------

if page == "⚡ Live SCADA Simulation":

    mode = st.radio(
    "Select Data Source",
    ["Dataset (1 Month)", "ESP32 Live"]
        )
    
    # ---------------------------
    # DATASET MODE
    # ---------------------------
    
    if mode == "Dataset (1 Month)":
        df = load_full_dataset()
        df.columns = df.columns.str.lower()
        # st.success("Dataset loaded: 1 month SCADA data")

        # 👉 KEEP YOUR ENTIRE EXISTING CODE HERE (NO CHANGE)

        st.subheader("Live SCADA Simulation ")


        # 🔥 Load full dataset
        df = load_full_dataset()

        # normalize column names (IMPORTANT)
        df.columns = df.columns.str.lower()

        st.success("Dataset loaded: 1 month SCADA data")

        # ---------------------------
        # SELECT FEATURE
        # ---------------------------
        selected_feature = st.selectbox(
            "Select Parameter",
            ["voltage", "current", "frequency"]
        )

        chart_placeholder = st.empty()

        # ---------------------------
        # SIMULATION BUTTON
        # ---------------------------
        if st.button("▶️ Run Full Simulation"):

            history = pd.DataFrame()

            window_size = 20

            total_points = len(df)
            total_anomalies = 0

            original_history = []
            recovered_history = []

            # Train once
            initial_data = df.iloc[:100]
            processed_df, _ = preprocess_data(initial_data)
            model_input = processed_df.select_dtypes(include=['float64', 'int64'])
            model = train_isolation_forest(model_input)

            logs = []

            # ---------------------------
            # ANOMALY TYPE CLASSIFIER
            # ---------------------------

            def classify_voltage_event(value):
                if value <= 20:   # increased threshold (more reliable)
                    return "Voltage Collapse"
                elif value < 150:
                    return "Voltage Dip"
                elif value > 260:
                    return "Voltage Swell"
                else:
                    return None

            detected_events = []
            event_triggered = False

            for i in range(0, len(df), window_size):

                chunk = df.iloc[i:i+window_size].reset_index(drop=True)
                raw_chunk = chunk.copy()

                processed_df, _ = preprocess_data(chunk)
                model_input = processed_df.select_dtypes(include=['float64', 'int64'])

                result_df = detect_anomalies(model, model_input)
                anomalies = result_df[result_df['final_anomaly'] == True]

                # ===========================
                # 🔥 FORCE COLLAPSE DETECTION (independent of ML)
                # ===========================

                for idx in range(len(raw_chunk)):
                    raw_value = raw_chunk.loc[idx, selected_feature]

                    if raw_value <= 20:
                    
                        if idx not in major_anomalies:
                            major_anomalies.append(idx)

                total_anomalies += len(anomalies)

                # 🔥 CLASSIFY SEVERITY
                minor_anomalies = []
                major_anomalies = []

                # for idx in anomalies.index:
                #     row = processed_df.loc[idx]

                #     numeric_values = pd.to_numeric(row, errors='coerce')

                #     if numeric_values.abs().max() > 3:
                #     # relaxed rule for minor (catch more cases)
                #     # if abs(row).max() > 3:   # strong deviation
                #         major_anomalies.append(idx)
                #     else:
                #         minor_anomalies.append(idx)

                for idx in anomalies.index:
                    row = processed_df.loc[idx]
                    numeric_values = pd.to_numeric(row, errors='coerce')

                    raw_value = raw_chunk.loc[idx, selected_feature]

                    # 🚨 FORCE collapse detection
                    if raw_value <= 20:
                        major_anomalies.append(idx)

                    elif numeric_values.abs().max() > 3:
                        major_anomalies.append(idx)

                    else:
                        minor_anomalies.append(idx)

                # HARDCODED DEMO WINDOW (14k–16k)
                # if 14900 <= i <= 15000 and not st.session_state.get("alert_shown", False):

                #     st.session_state["alert_shown"] = True

                #     st.toast("🚨 Major Voltage Collapse Detected!", icon="🚨")
                #     time.sleep(3)

                #     st.toast("✅ System Stabilized - Anomaly Resolved", icon="✅")

                # if major_anomalies:
                #     st.toast("🚨 Major anomaly detected!", icon="🚨")
                #     time.sleep(2)

                # ---------------------------
                # EXPLAIN + LOG
                # ---------------------------
                for idx in anomalies.index:
                    explanation = explain_anomaly(chunk, idx)
                    logs.append(f"Anomaly at {i+idx}: {explanation}")

                # ---------------------------
                # Major Anomaly Event Detection
                # ---------------------------

                for idx in major_anomalies:

                    # absolute_index = len(history)
                    absolute_index = len(history) - len(raw_chunk) + idx

                    value = raw_chunk.loc[idx, selected_feature]
                    event_type = classify_voltage_event(value)

                    if event_type:
                    
                        # Prevent duplicate triggers
                        # if not event_triggered:
                        if event_type not in [e["type"] for e in detected_events]:
                        
                            event_triggered = True

                            # 🔔 TOAST
                            st.toast(f"🚨 {event_type} Detected!", icon="🚨")
                            time.sleep(2)
                            st.toast("✅ System Stabilized", icon="✅")

                            # 📌 Store event center
                            detected_events.append({
                                "type": event_type,
                                "index": absolute_index
                            })

                # ---------------------------
                # APPLY RESPONSE
                # ---------------------------
                recovered_chunk = apply_response(chunk, anomalies)

                original_history.append(raw_chunk.copy())
                recovered_history.append(recovered_chunk.copy())

                # ---------------------------
                # STORE HISTORY
                # ---------------------------
                history = pd.concat([history, raw_chunk], ignore_index=True)

                # ---------------------------
                # PLOT (SLIDING WINDOW)
                # ---------------------------
                display_df = history.tail(100)

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    # x=range(len(display_df)),
                    x=display_df.index,
                    y=display_df[selected_feature],
                    mode='lines',
                    name="Live Data"
                ))

                fig.update_layout(
                    template="plotly_dark",
                    xaxis_title="Time (Data Points)",
                    yaxis_title=selected_feature.capitalize(),
                    title=f"{selected_feature.capitalize()} Live Monitoring"
                )

                # 🟡 Minor anomalies
                if minor_anomalies:
                    fig.add_trace(go.Scatter(
                        x=[len(history) - len(raw_chunk) + idx for idx in minor_anomalies],
                        y=raw_chunk.loc[minor_anomalies, selected_feature],
                        mode='markers',
                        name='Minor',
                        marker=dict(color='yellow', size=6)
                    ))

                # 🔴 Major anomalies
                if major_anomalies:
                    fig.add_trace(go.Scatter(
                        x=[len(history) - len(raw_chunk) + idx for idx in major_anomalies],
                        y=raw_chunk.loc[major_anomalies, selected_feature],
                        mode='markers',
                        # name='Major',
                        name='Anomaly',
                        marker=dict(color='red', size=10)
                    ))

                chart_placeholder.plotly_chart(fig, use_container_width=True)

                time.sleep(0.1)

                if len(major_anomalies) == 0:
                    event_triggered = False

            st.success("Simulation Completed")


            # ---------------------------
            # FINAL FULL TIMELINE GRAPH
            # ---------------------------

            final_fig = go.Figure()

            final_fig.add_trace(go.Scatter(
                x=history.index,
                y=history[selected_feature],
                mode='lines',
                name="Full Timeline"
            ))

            final_fig.update_layout(
                template="plotly_dark",
                title="Full SCADA Timeline",
                xaxis_title="Time (Data Points)",
                yaxis_title=selected_feature.capitalize(),
                xaxis=dict(rangeslider=dict(visible=True))
            )

            st.plotly_chart(final_fig, use_container_width=True)


            original_df = pd.concat(original_history, ignore_index=True)
            recovered_df = pd.concat(recovered_history, ignore_index=True)


            # ---------------------------
            # RECOVERY GRAPH
            # ---------------------------

            # ---------------------------
            # FALLBACK: ENSURE COLLAPSE EXISTS
            # ---------------------------

            collapse_exists = any(e["type"] == "Voltage Collapse" for e in detected_events)

            if not collapse_exists:
            
                # find first 0V point
                collapse_idx = original_df[original_df[selected_feature] <= 5].index

                if len(collapse_idx) > 0:
                    detected_events.append({
                        "type": "Voltage Collapse",
                        "index": int(collapse_idx[0])
                    })

            st.subheader("Anomaly Recovery Analysis")

            for event in detected_events:
            
                center = event["index"]

                start = max(0, center - 1000)
                end = min(len(original_df), center + 1000)

                zoom_original = original_df.iloc[start:end].reset_index(drop=True)
                zoom_recovered = recovered_df.iloc[start:end].reset_index(drop=True)

                fig = go.Figure()

                # ---------------------------
                # SPECIAL CASE: COLLAPSE
                # ---------------------------
                if event["type"] == "Voltage Collapse":
                
                    fig.add_trace(go.Scatter(
                        x=zoom_original.index,
                        y=zoom_original[selected_feature],
                        name="System Collapse (0V)",
                        line=dict(color='#D62728', width=3)
                    ))

                    fig.add_trace(go.Scatter(
                        x=zoom_recovered.index,
                        y=zoom_recovered[selected_feature],
                        name="System Restoration",
                        line=dict(color='#2CA02C', width=3)
                    ))

                    # Highlight blackout region
                    collapse_zone = zoom_original[zoom_original[selected_feature] <= 5]

                    fig.add_trace(go.Scatter(
                        x=collapse_zone.index,
                        y=collapse_zone[selected_feature],
                        mode='markers',
                        name='Blackout Zone',
                        marker=dict(color='#000000', size=6)
                    ))

                    fig.update_layout(
                        template="plotly_dark",
                        title="⚡ Voltage Collapse & System Restoration",
                        xaxis_title="Time Window (~2000 points)",
                        yaxis_title="Voltage"
                    )

                # ===========================
                # NORMAL (Dip / Swell)
                # ===========================
                else:
                
                    fig.add_trace(go.Scatter(
                        x=zoom_original.index,
                        y=zoom_original[selected_feature],
                        name="Original (With Attack)",
                        line=dict(color='#D62728', dash='dot')
                    ))

                    fig.add_trace(go.Scatter(
                        x=zoom_recovered.index,
                        y=zoom_recovered[selected_feature].rolling(5).mean(),
                        name="Recovered System",
                        line=dict(color='#2CA02C')
                    ))

                    # attack point
                    signal = zoom_original[selected_feature]
                    attack_idx = signal.idxmin()

                    # fig.add_trace(go.Scatter(
                    #     x=[attack_idx],
                    #     y=[signal.iloc[attack_idx]],
                    #     mode='markers',
                    #     name='Attack Point',
                    #     marker=dict(color='yellow', size=12, symbol='x')
                    # ))

                    fig.update_layout(
                        template="plotly_dark",
                        title=f"⚡ {event['type']} Recovery",
                        xaxis_title="Time Window (~2000 points)",
                        yaxis_title="Voltage"
                    )

                st.plotly_chart(fig, use_container_width=True)


            # ---------------------------
            # FINAL EXPLANATION
            # ---------------------------
            # st.subheader("What Happened?")

            st.markdown("""
            ### Major Anomaly Detection and Recovery Analysis

            ---

            ## Event Overview

            During the simulation of one month of SCADA data, the system encountered three major types of anomalies:

            - Voltage Dip (sudden reduction in voltage level)
            - Voltage Swell (temporary overvoltage condition)
            - Voltage Collapse (complete loss of voltage supply)

            These anomalies represent different classes of disturbances, ranging from operational fluctuations to critical system failures.

            ---

            ## Detection Methodology

            The system uses a hybrid detection approach combining multiple techniques:

            ### 1. Machine Learning-Based Detection
            An Isolation Forest model is trained on normal operating conditions. It identifies anomalous data points based on deviations in multidimensional feature space, considering voltage, current, and frequency together.

            ### 2. Statistical Validation
            Z-score based validation is applied to detect extreme deviations from normal behavior. This ensures that subtle anomalies are not missed and false positives are reduced.

            ### 3. Rule-Based Override for Critical Events
            Certain critical conditions, such as voltage collapse (near-zero voltage), are detected using rule-based logic. This ensures that rare but high-impact events are always captured, even if machine learning models fail to detect them due to limited occurrence.

            ---

            ## Types of Anomalies Observed

            ### Voltage Dip

            A voltage dip is characterized by a temporary reduction in voltage, typically caused by sudden load changes or system disturbances.

            System Behavior:
            - Voltage drops significantly below nominal levels (~220V)
            - System remains operational
            - Sensitive equipment may malfunction

            Recovery:
            - The recovery system applies smoothing and correction using recent stable values
            - Voltage is gradually restored to normal levels
            - No abrupt transitions are introduced, maintaining system stability

            ---

            ### Voltage Swell

            A voltage swell represents a temporary increase in voltage beyond safe limits, often caused by sudden load disconnection or switching events.

            System Behavior:
            - Voltage rises above normal operating range (>260V)
            - Can stress or damage electrical equipment

            Recovery:
            - The system detects overvoltage conditions
            - Applies controlled normalization to bring voltage back to safe levels
            - Stabilization occurs smoothly without oscillations

            ---

            ### Voltage Collapse

            Voltage collapse is a critical condition where the system voltage drops to near zero, indicating a failure or blackout scenario.

            System Behavior:
            - Voltage drops to 0V (or near-zero)
            - Represents loss of supply or severe fault condition
            - System becomes non-operational during this period

            Recovery Behavior:
            - Unlike dip and swell, collapse is not corrected smoothly
            - The system shows a flatline region representing outage
            - Restoration occurs as a step change when power is reintroduced
            - Followed by gradual stabilization back to nominal levels

            This distinction is important, as collapse represents a system-level failure rather than a controllable fluctuation.

            ---

            ## Response and Recovery Strategy

            The system implements an adaptive recovery mechanism:

            1. Detection
               - Anomalies are detected in real-time using hybrid methods

            2. Classification
               - Events are categorized into dip, swell, or collapse based on severity and physical characteristics

            3. Response
               - Minor anomalies are smoothed
               - Major anomalies trigger alerts and corrective action

            4. Recovery
               - For dip and swell: gradual correction using historical trends
               - For collapse: restoration-based recovery (not continuous correction)

            ---

            ## Impact on SCADA System

            Each anomaly type affects the system differently:

            - Voltage Dip:
              - Causes temporary instability
              - May affect sensitive equipment performance

            - Voltage Swell:
              - Can lead to overheating or damage
              - Requires immediate normalization

            - Voltage Collapse:
              - Results in complete system outage
              - Requires external restoration mechanisms
              - Highest severity among all anomalies

            ---

            ## Summary

            This system demonstrates a complete anomaly handling pipeline:

            Detection → Classification → Response → Recovery → Visualization

            Key observations:

            - Hybrid detection improves reliability and robustness
            - Different anomalies require different recovery strategies
            - Voltage collapse cannot be treated like standard anomalies and must be handled as a system restoration event
            - Real-time monitoring combined with adaptive recovery can significantly enhance SCADA system resilience

            ---

            ## Conclusion

            The implementation shows how intelligent monitoring systems can not only detect anomalies but also respond appropriately based on their nature. By distinguishing between operational disturbances and critical failures, the system ensures both accuracy and practical relevance for real-world SCADA environments.
        """)

    # ---------------------------
    # 🔌 ESP32 LIVE MODE
    # ---------------------------
    elif mode == "ESP32 Live":

        st.success("ESP32 Live Mode Activated")

        import serial

        import serial.tools.list_ports

        ports = [port.device for port in serial.tools.list_ports.comports()]

        # selected_port = st.selectbox("Select ESP32 Port", ports)     
        # if not ports:
        #     st.error("No ESP32 detected. Please connect device.")   

        # # ser = serial.Serial('/dev/tty.usbserial-0001', 115200)
        # ser = serial.Serial(selected_port, 115200)

        if ports:
            selected_port = st.selectbox("Select ESP32 Port", ports)
            ser = serial.Serial(selected_port, 115200)
        else:
            st.error("No ESP32 detected")
            st.stop()

        if "live_data" not in st.session_state:
            st.session_state.live_data = pd.DataFrame(
                columns=["voltage", "current", "frequency"]
            )

        chart_placeholder = st.empty()


        if st.button("▶️ Start ESP32 Live"):

            st.session_state.run_esp = True

        if "run_esp" not in st.session_state:
            st.session_state.run_esp = False

        if st.session_state.run_esp:
        
            value = None
            try:
                value = float(ser.readline().decode().strip())
            except:
                pass
            
            if value is not None:
                new_row = pd.DataFrame({
                    "voltage": [value],
                    "current": [value * 0.1],
                    "frequency": [50]
                })

                st.session_state.live_data = pd.concat(
                    [st.session_state.live_data, new_row],
                    ignore_index=True
                )

            df_live = st.session_state.live_data.tail(100)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_live.index,
                y=df_live["voltage"],
                mode='lines',
                name="Live Voltage"
            ))

            chart_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(1)
            st.rerun()

# ---------------------------
# PROCESS DATA
# ---------------------------

if uploaded_files:

    all_results = []
    original_dfs = []

    with st.spinner(" Processing datasets..."):

        for file in uploaded_files:
            df = pd.read_csv(file)
            original_dfs.append(df)

            processed_df, _ = preprocess_data(df)
            model_input = processed_df.select_dtypes(include=['float64', 'int64'])

            model = train_isolation_forest(model_input)
            result_df = detect_anomalies(model, model_input)

            # ---------------------------
            # SMART CLASSIFICATION
            # ---------------------------           

            def classify_voltage_event(value):
                if value <= 20:
                    return "Voltage Collapse"
                elif value < 150:
                    return "Voltage Dip"
                elif value > 250:
                    return "Voltage Swell"
                else:
                    return None         

            result_df["event_type"] = None
            result_df["severity"] = "Normal"            

            for idx in result_df.index:         

                raw_value = df.loc[idx, "voltage"]          

                # Rule-based detection (VERY IMPORTANT)
                event = classify_voltage_event(raw_value)           

                if event:
                    result_df.loc[idx, "event_type"] = event
                    result_df.loc[idx, "severity"] = "Major"            

                elif result_df.loc[idx, "final_anomaly"]:
                    result_df.loc[idx, "severity"] = "Minor"            

            result_df['source'] = file.name
            all_results.append(result_df)  

        # ===========================
        # FORCE DETECTION OF COLLAPSE EVENTS (CRITICAL FIX)
        # ===========================
        collapse_indices = df[df["voltage"] <= 20].index

        for idx in collapse_indices:
            result_df.loc[idx, "event_type"] = "Voltage Collapse"
            result_df.loc[idx, "severity"] = "Major"         


        combined_df = pd.concat(all_results)
        df = original_dfs[0]            

        patterns = detect_patterns(combined_df)
        risk = classify_risk(combined_df, patterns)

# ---------------------------
# DASHBOARD 
# ---------------------------
if page == "📊 Dashboard" and uploaded_files:

    st.subheader(" Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("---")

    st.subheader(" System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(combined_df))
    col2.metric("Anomalies", int(combined_df['final_anomaly'].sum()))
    col3.metric("Patterns", len(patterns))

    # ===========================
    #
    # ===========================
    st.subheader("Detected Event Types")

    event_counts = combined_df["event_type"].value_counts()

    st.write(event_counts)


    selected_feature = st.selectbox(
        "Select Parameter to Visualize",
        # ["Voltage", "Current", "Frequency"]
        ["voltage", "current", "frequency"]
    )

    # Placeholders for live updates
    chart_placeholder = st.empty()
    status_placeholder = st.empty()



# ---------------------------
# 📈 GRAPH (STATIC + LIVE MODE)
# ---------------------------
    st.subheader(f"📈 {selected_feature.capitalize()} Monitoring")

    chart_placeholder = st.empty()

# ---------------------------
# 🔴 LIVE MODE
# ---------------------------
    if st.session_state.start_sim:

        # st.info("🔴 Live Simulation Mode Enabled")

        live_df = df.copy()

        original_history = []
        recovered_history = []

        window_size = 20

        # 🔥 Train model ONCE on initial data
        initial_data = live_df.iloc[:100]

        processed_df, _ = preprocess_data(initial_data)
        model_input = processed_df.select_dtypes(include=['float64', 'int64'])

        model = train_isolation_forest(model_input)

        if "history_df" not in st.session_state:
            st.session_state.history_df = pd.DataFrame()

        for i in range(0, len(live_df), window_size):

            # 🟢 get ONLY new data chunk
            current_chunk = stream_data(live_df, i, window_size)
            current_chunk = current_chunk.reset_index(drop=True)
 
            raw_chunk = current_chunk.copy()

            if current_chunk.empty:
                break

            # 🔵 STORE ORIGINAL
            original_history.append(raw_chunk.copy())

            processed_df, _ = preprocess_data(current_chunk)
            model_input = processed_df.select_dtypes(include=['float64', 'int64'])

            result_df = detect_anomalies(model, model_input)

            anomalies = result_df[result_df['final_anomaly'] == True]

            global_idx = len(st.session_state.history_df) - len(raw_chunk) + idx

            # event_type = classify_voltage_event(raw_chunk.loc[idx, "voltage"])

            # 🔥 EXPLAIN FIRST
            if not anomalies.empty:
                for idx in anomalies.index:
                    explanation = explain_anomaly(current_chunk, idx)
                    severity = " Major" if "abnormal" in str(explanation) else " Minor"

                    st.session_state.logs = log_event(
                        st.session_state.logs,                   
                        # f"{severity} anomaly at {idx}: {explanation}"

                        f"{severity} anomaly at {global_idx}: {explanation}"
                        # f"[{severity}] {event_type or 'General Anomaly'} at {global_idx}: {explanation}"
                        )
                # for idx in anomalies.index:

                #     explanation = explain_anomaly(current_chunk, idx)

                #     global_idx = len(st.session_state.history_df) - len(raw_chunk) + idx

                #     if idx in major_anomalies:
                #         severity = "MAJOR"
                #     else:
                #         severity = "MINOR"

                #     st.session_state.logs = log_event(
                #         st.session_state.logs,
                #         f"{severity} anomaly at {global_idx}: {explanation}"
                #     )

                # 🔥 APPLY RESPONSE
                current_chunk = apply_response(current_chunk, anomalies)

            # 🟢 STORE RECOVERED
            recovered_history.append(current_chunk.copy())

            # 🔥 ADD TO HISTORY (CRITICAL FIX)
            st.session_state.history_df = pd.concat(
                [st.session_state.history_df, raw_chunk],
                ignore_index=True
            )




    # --- RESPONSE SYSTEM ----

            fig = go.Figure()

            history = st.session_state.history_df
            # history = st.session_state.history_df.tail(100)

            if history.empty or selected_feature not in history.columns:
                continue

            fig.add_trace(go.Scatter(
                x=history.index,
                # x=range(len(history)),
                y=history[selected_feature],
                mode='lines',
                name="Live Data",
                line=dict(color='#00BFFF')
            ))

            # 🔥 Map anomaly positions correctly
            anomaly_positions = anomalies.index.tolist()

            fig.add_trace(go.Scatter(
                x=[len(st.session_state.history_df) - len(raw_chunk) + idx for idx in anomaly_positions],
                y=raw_chunk.loc[anomaly_positions, selected_feature],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=8)
            ))

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Time",
                yaxis_title=selected_feature.capitalize(),
                height=500
            )

            chart_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)

# ---------------------------
# ⚡ STATIC MODE (DEFAULT)
# ---------------------------
    else:

        # st.info("⚡ Static Analysis Mode")

        x_axis = df['Timestamp'] if 'Timestamp' in df.columns else df.index

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_axis,
            y=df[selected_feature],
            mode='lines',
            name="Normal",
            line=dict(color='#00BFFF', width=2)
        ))

        # anomalies = combined_df[combined_df['final_anomaly'] == True]
        major = combined_df[combined_df["severity"] == "Major"]
        minor = combined_df[combined_df["severity"] == "Minor"]


        # Minor
        fig.add_trace(go.Scatter(
            x=x_axis[minor.index],
            y=df.loc[minor.index, selected_feature],
            mode='markers',
            name='Minor Anomalies',
            marker=dict(color='yellow', size=6)
        ))

        # Major
        fig.add_trace(go.Scatter(
            x=x_axis[major.index],
            y=df.loc[major.index, selected_feature],
            mode='markers',
            name='Major Anomalies',
            marker=dict(color='red', size=10)
        ))

        fig.update_xaxes(rangeslider_visible=True)

        chart_placeholder.plotly_chart(fig, use_container_width=True)


# ---------------------------
# LOGS
# ---------------------------


    st.subheader("📜 Event Logs")

    # for log in st.session_state.logs[-5:]:
    #     st.write(log)

    for log in st.session_state.logs[-5:]:

        if "MAJOR" in log:
            st.error(log)
        else:
            st.warning(log)

    st.markdown("---")
    # st.subheader("🔄 Before vs After Recovery")

    if st.session_state.start_sim and original_history and recovered_history:

    # 🔥 THIS is the line you were asking about
        original_df = pd.concat(original_history, ignore_index=True)
        recovered_df = pd.concat(recovered_history, ignore_index=True)

        fig_compare = go.Figure()

        # 🔴 Original (with anomaly)
        fig_compare.add_trace(go.Scatter(
            x=original_df.index,
            y=original_df[selected_feature],
            mode='lines',
            name="Original (With Anomaly)",
            line=dict(color='red', dash='dot')
        ))

        # 🟢 Recovered (after response)
        fig_compare.add_trace(go.Scatter(
            x=recovered_df.index,
            # y=recovered_df[selected_feature],
            y=recovered_df[selected_feature].rolling(5).mean(),
            mode='lines',
            name="Recovered (After Response)",
            line=dict(color='green')
        ))

        fig_compare.update_layout(
            template="plotly_dark",
            title="System Recovery After Attack",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            height=500
        )

        st.plotly_chart(fig_compare, use_container_width=True)



# ---------------------------
# HEATMAP (CORRELATION)
# ---------------------------

    # # Advanced Heatmap
    # st.subheader("Feature-wise Correlation Heatmap")

    # numeric_cols = combined_df.select_dtypes(include=['float64', 'int64']).columns
    # heatmap_matrix = combined_df[numeric_cols].corr()

    # fig_heat = px.imshow(
    #     heatmap_matrix,
    #     text_auto=True,
    #     color_continuous_scale='RdBu_r'
    # )

    # fig_heat.update_layout(template="plotly_dark")

    # st.plotly_chart(fig_heat, use_container_width=True)

    # st.markdown("---")



# ---------------------------
#  ATTACK TIMELINE
# ---------------------------

    st.subheader("🧭 Attack Timeline")

    timeline = combined_df.copy()

    timeline['time'] = range(len(timeline))
    
    # Binary anomaly signal (THIS IS KEY)
    timeline['anomaly'] = timeline['final_anomaly'].astype(int)
    
    fig_timeline = go.Figure()
    
    # ---------------------------
    # BASELINE (flat 0 line)
    # ---------------------------
    fig_timeline.add_trace(go.Scatter(
        x=timeline['time'],
        y=[0]*len(timeline),
        mode='lines',
        name='Normal',
        line=dict(color='#7F7F7F', width=1)
    ))
    
    # ---------------------------
    # ANOMALY SPIKES (THIS CREATES PATTERN)
    # ---------------------------
    fig_timeline.add_trace(go.Scatter(
        x=timeline['time'],
        y=timeline['anomaly'],
        mode='markers',
        name='Anomalies',
        marker=dict(
            color='#D62728',
            size=6
        )
    ))
    
    fig_timeline.update_layout(
        template="plotly_dark",
        title="SCADA Attack Timeline (Pattern View)",
        xaxis_title="Time",
        yaxis_title="Anomaly Occurrence (0 / 1)",
        yaxis=dict(range=[-0.2, 1.2])
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("---")

# ---------------------------
#  RISK ANALYSIS
# ---------------------------

    ### Risk Gauge ###
    risk_score = calculate_risk_score(combined_df, patterns)

    st.subheader("⚠️ Risk Score")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': "System Risk Level"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red"},
            'steps': [
                {'range': [0, 30], 'color': "green"},
                {'range': [30, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "red"}
            ],
        }
    ))

    st.plotly_chart(gauge, use_container_width=True)

    if risk_score > 70:
        st.error("🔴 HIGH RISK - Immediate Action Required")
    elif risk_score > 30:
        st.warning("🟡 MEDIUM RISK - Monitor Closely")
    else:
        st.success("🟢 LOW RISK - System Stable")

    st.markdown("---")



# ---------------------------
# ALERTS 
# ---------------------------



if page == "🚨 Alerts" and uploaded_files:

    st.subheader("🚨 Detected Threat Patterns")

    st.markdown("### Intelligent System Observation Panel")

    # ---------------------------
    # SYSTEM STATISTICS
    # ---------------------------
    risk_score = calculate_risk_score(combined_df, patterns)
    total_records = len(combined_df)

    total_anomalies = int(combined_df['final_anomaly'].sum())

    major_events = combined_df[combined_df["severity"] == "Major"]
    minor_events = combined_df[combined_df["severity"] == "Minor"]

    major_count = len(major_events)
    minor_count = len(minor_events)

    event_counts = combined_df["event_type"].value_counts()

    dominant_event = (
        event_counts.idxmax()
        if not event_counts.empty
        else "No Major Event"
    )

    anomaly_ratio = round((total_anomalies / total_records) * 100, 2)

    # ---------------------------
    # SYSTEM HEALTH STATUS
    # ---------------------------
    if risk_score > 70:
        system_status = "CRITICAL"
    elif risk_score > 40:
        system_status = "WARNING"
    else:
        system_status = "STABLE"

    # ---------------------------
    # TOP OBSERVATION CARD
    # ---------------------------
    st.error(f"""
    System Status: {system_status}

    Detected Anomalies: {total_anomalies}

    Major Events: {major_count}

    Minor Events: {minor_count}

    Dominant Threat Pattern: {dominant_event}

    Anomaly Density: {anomaly_ratio}% of total system activity
    """)

    # ---------------------------
    # DETAILED THREAT ANALYSIS
    # ---------------------------
    st.markdown("### Threat Interpretation")

    # Voltage Collapse
    if "Voltage Collapse" in event_counts.index:

        collapse_count = event_counts["Voltage Collapse"]

        with st.expander("Voltage Collapse Analysis", expanded=True):

            st.error(f"""
    Critical voltage collapse events detected: {collapse_count}

    Observations:
    - Near-zero voltage conditions identified
    - Indicates possible blackout or severe instability
    - SCADA visibility may be partially lost during collapse

    Operational Impact:
    - Equipment shutdown risk
    - Protection relay activation
    - Grid instability possibility

    Recommended Response:
    - Verify restoration sequence
    - Inspect feeder isolation
    - Validate breaker and relay coordination
    """)

    # Voltage Dip
    if "Voltage Dip" in event_counts.index:

        dip_count = event_counts["Voltage Dip"]

        with st.expander("Voltage Dip Analysis"):

            st.warning(f"""
    Voltage dip events detected: {dip_count}

    Observations:
    - Temporary undervoltage conditions identified
    - System remained operational during disturbance

    Operational Impact:
    - Sensitive load instability
    - Possible motor performance degradation

    Recommended Response:
    - Inspect load fluctuations
    - Verify transformer tap settings
    - Monitor recurring dip patterns
    """)

    # Voltage Swell
    if "Voltage Swell" in event_counts.index:

        swell_count = event_counts["Voltage Swell"]

        with st.expander("Voltage Swell Analysis"):

            st.warning(f"""
    Voltage swell events detected: {swell_count}

    Observations:
    - Temporary overvoltage conditions observed
    - Indicates possible switching disturbance or load rejection

    Operational Impact:
    - Overheating risk
    - Equipment stress conditions

    Recommended Response:
    - Verify voltage regulation system
    - Inspect capacitor bank operations
    - Monitor switching sequences
    """)

    # ---------------------------
    # PATTERN ANALYSIS
    # ---------------------------
    st.markdown("### Pattern Intelligence")

    for p in patterns:

        if "Burst anomaly" in p:

            st.info(f"""
    Pattern Detected: Coordinated Burst Activity

    Interpretation:
    Multiple anomalies occurred in a compressed time window,
    indicating structured or cascading disturbance behavior.

    Possible Causes:
    - Coordinated cyber intrusion
    - Fast load oscillation
    - Cascading system instability
    """)

        elif "sensor freeze" in p:

            st.info(f"""
    Pattern Detected: Sensor Freeze / Data Stagnation

    Interpretation:
    Sensor values remained constant for abnormal duration.

    Possible Causes:
    - Sensor malfunction
    - Communication issue
    - Data spoofing attempt
    """)

        elif "voltage manipulation" in p:

            st.info(f"""
    Pattern Detected: Voltage Manipulation

    Interpretation:
    Abnormal voltage behavior inconsistent with normal operating profile.

    Possible Causes:
    - False data injection
    - Unauthorized control action
    - Switching instability
    """)

    # ---------------------------
    # FINAL OPERATOR SUMMARY
    # ---------------------------
    st.markdown("### Operator Recommendation")

    if system_status == "CRITICAL":

        st.error("""
    Immediate operator intervention recommended.

    The system is currently experiencing high-severity disturbances
    that may affect operational stability and equipment safety.
    """)

    elif system_status == "WARNING":

        st.warning("""
    System instability indicators detected.

    Continuous monitoring and preventive inspection are recommended
    to avoid escalation into critical failure.
    """)

    else:

        st.success("""
    System behavior remains within acceptable operational limits.

    No immediate intervention required. Continue monitoring.
    """)

    st.markdown("---")

    # Summary Table
    st.subheader("📊 Alert Summary")

    summary_data = {
        "Metric": ["Total Records", "Anomalies Detected", "Patterns Found"],
        "Value": [
            len(combined_df),
            int(combined_df['final_anomaly'].sum()),
            len(patterns)
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

# ---------------------------
# REPORT
# ---------------------------
if page == "📋 Report" and uploaded_files:

    st.subheader("📋 Report")

    anomaly_data = combined_df[combined_df['final_anomaly'] == True]

    st.dataframe(anomaly_data, use_container_width=True)

    csv = anomaly_data.to_csv(index=False)

    st.download_button("Download Report", csv, "report.csv")

# ---------------------------
# NO DATA
# ---------------------------
# if not uploaded_files:
#     st.info("⬅️ Upload dataset(s) from sidebar")













