#!/usr/bin/env python3
"""
Streamlit App for Traffic Tamer
Web-based interactive dashboard
"""

import streamlit as st
import yaml
import time
import numpy as np
from traffic_tamer.environment import TrafficEnvironment
from traffic_tamer.agents import AgentManager
from traffic_tamer.analytics import Analytics
from traffic_tamer.dashboard import StreamlitDashboard


# Page configuration
st.set_page_config(
    page_title="Traffic Tamer - Multi-Agent Simulation",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    st.session_state.config = config
    st.session_state.env = TrafficEnvironment(config)
    st.session_state.agent_manager = AgentManager(config)
    st.session_state.analytics = Analytics(config)
    st.session_state.dashboard = StreamlitDashboard()
    st.session_state.metrics_history = []
    st.session_state.running = False
    st.session_state.step = 0
    st.session_state.initialized = True

# Main app
def main():
    dashboard = st.session_state.dashboard
    env = st.session_state.env
    agent_manager = st.session_state.agent_manager
    analytics = st.session_state.analytics
    
    # Render header
    dashboard.render_header()
    
    # Render controls
    controls = dashboard.render_controls(st.session_state.config)
    
    # Handle control actions
    if controls['reset']:
        env.reset()
        st.session_state.metrics_history = []
        st.session_state.step = 0
        analytics.reset()
        st.session_state.running = False
        st.success("Simulation reset!")
    
    if controls['start']:
        st.session_state.running = True
        # Setup simulation
        num_vehicles = controls['num_vehicles']
        agent_type = controls['agent_type']
        
        env.reset()
        st.session_state.metrics_history = []
        
        # Spawn vehicles
        for i in range(num_vehicles):
            if agent_type == 'selfish':
                veh_type = 'selfish'
            elif agent_type == 'cooperative':
                veh_type = 'cooperative'
            else:  # mixed
                veh_type = 'selfish' if i < num_vehicles // 2 else 'cooperative'
            
            agent = agent_manager.create_agent(veh_type)
            env.spawn_vehicle(agent_type=veh_type)
        
        st.success(f"Started simulation with {num_vehicles} {agent_type} vehicles!")
    
    if controls['pause']:
        st.session_state.running = False
        st.info("Simulation paused")
    
    # Render info panel
    dashboard.render_info_panel()
    
    # Create main content area
    st.markdown("---")
    
    # Get current metrics
    metrics = env._collect_metrics()
    analytics_summary = analytics.get_system_performance_summary()
    
    # Render metrics
    dashboard.render_metrics(metrics, analytics_summary)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analytics",
        "🗺️ Network",
        "📉 Time Series",
        "🔍 Braess's Paradox"
    ])
    
    with tab1:
        dashboard.render_price_of_anarchy(analytics_summary)
        st.markdown("---")
        dashboard.render_comparison_chart(analytics)
    
    with tab2:
        dashboard.render_network_visualization(env)
    
    with tab3:
        dashboard.render_time_series(st.session_state.metrics_history)
    
    with tab4:
        dashboard.render_braess_paradox(analytics)
    
    # Run simulation step if running
    if st.session_state.running:
        # Step simulation
        metrics = env.step()
        
        # Move vehicles
        for vehicle_id, vehicle in list(env.vehicles.items()):
            if vehicle['completed']:
                continue
            
            # Get agent
            agent = None
            for a in agent_manager.agents.values():
                if a.agent_type == vehicle['agent_type']:
                    agent = a
                    break
            
            if agent:
                next_pos = agent.get_action(env, vehicle_id)
                if next_pos is not None:
                    env.move_vehicle(vehicle_id, next_pos)
        
        # Record metrics
        st.session_state.metrics_history.append(metrics)
        analytics.record_metrics(metrics, controls['agent_type'])
        
        st.session_state.step += 1
        
        # Respawn vehicles if needed
        if len(env.vehicles) < controls['num_vehicles']:
            if np.random.random() < st.session_state.config['simulation']['spawn_rate']:
                agent_type = controls['agent_type']
                if agent_type == 'mixed':
                    veh_type = 'selfish' if np.random.random() < 0.5 else 'cooperative'
                else:
                    veh_type = agent_type
                
                agent = agent_manager.create_agent(veh_type)
                env.spawn_vehicle(agent_type=veh_type)
        
        # Auto-refresh
        time.sleep(1.0 / controls['speed'])
        st.rerun()


if __name__ == '__main__':
    main()
