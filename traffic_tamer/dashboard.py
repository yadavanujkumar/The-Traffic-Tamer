"""
Streamlit Dashboard
Web-based visualization and control interface
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List


class StreamlitDashboard:
    """Streamlit-based dashboard for traffic simulation"""
    
    def __init__(self):
        st.set_page_config(
            page_title="Traffic Tamer - Multi-Agent Simulation",
            page_icon="🚗",
            layout="wide"
        )
        
    def render_header(self):
        """Render dashboard header"""
        st.title("🚗 Traffic Tamer: Multi-Agent Traffic Simulation")
        st.markdown("""
        **Game Theory meets Reinforcement Learning**
        
        Compare *Selfish* (Nash Equilibrium) vs *Cooperative* (Social Optimum) driving behaviors
        """)
        
    def render_controls(self, config: Dict) -> Dict:
        """Render simulation controls"""
        st.sidebar.header("Simulation Controls")
        
        # Traffic density selection
        density = st.sidebar.selectbox(
            "Traffic Density",
            ["low", "medium", "high", "rush_hour", "midnight"],
            index=1
        )
        
        # Agent type selection
        agent_type = st.sidebar.selectbox(
            "Agent Type",
            ["selfish", "cooperative", "mixed"],
            index=2
        )
        
        # Number of vehicles
        num_vehicles = st.sidebar.slider(
            "Number of Vehicles",
            min_value=10,
            max_value=100,
            value=50,
            step=5
        )
        
        # Simulation speed
        speed = st.sidebar.slider(
            "Simulation Speed",
            min_value=1,
            max_value=10,
            value=5
        )
        
        # Control buttons
        col1, col2, col3 = st.sidebar.columns(3)
        start = col1.button("▶️ Start")
        pause = col2.button("⏸️ Pause")
        reset = col3.button("🔄 Reset")
        
        return {
            'density': density,
            'agent_type': agent_type,
            'num_vehicles': num_vehicles,
            'speed': speed,
            'start': start,
            'pause': pause,
            'reset': reset
        }
    
    def render_metrics(self, metrics: Dict, analytics_summary: Dict):
        """Render key metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Vehicles",
                metrics.get('active_vehicles', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "Completed Vehicles",
                metrics.get('completed_vehicles', 0),
                delta=None
            )
        
        with col3:
            st.metric(
                "Avg Wait Time",
                f"{metrics.get('avg_wait_time', 0):.2f}s",
                delta=None
            )
        
        with col4:
            st.metric(
                "Avg Congestion",
                f"{metrics.get('avg_congestion', 0):.1%}",
                delta=None
            )
    
    def render_price_of_anarchy(self, analytics_summary: Dict):
        """Render Price of Anarchy visualization"""
        st.subheader("📊 Price of Anarchy (PoA)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            **Current PoA: {analytics_summary.get('current_poa', 1.0):.3f}**
            
            - PoA = 1.0: Selfish and Cooperative strategies are equally efficient
            - PoA > 1.0: Selfish behavior reduces system efficiency
            - Higher PoA indicates greater cost of selfish behavior
            """)
        
        with col2:
            # PoA gauge
            poa_value = analytics_summary.get('current_poa', 1.0)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=poa_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "PoA"},
                gauge={
                    'axis': {'range': [0.5, 2.0]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0.5, 1.05], 'color': "lightgreen"},
                        {'range': [1.05, 1.5], 'color': "yellow"},
                        {'range': [1.5, 2.0], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1.5
                    }
                }
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_comparison_chart(self, analytics):
        """Render comparison between selfish and cooperative agents"""
        st.subheader("📈 Strategy Comparison")
        
        comparison = analytics.get_comparative_analysis()
        
        if comparison:
            # Create comparison dataframe
            metrics_df = pd.DataFrame({
                'Metric': ['Travel Time', 'Wait Time', 'Completed', 'Congestion'],
                'Selfish': [
                    comparison['selfish_average']['travel_time'],
                    comparison['selfish_average']['wait_time'],
                    comparison['selfish_average']['completed'],
                    comparison['selfish_average']['congestion'] * 100
                ],
                'Cooperative': [
                    comparison['cooperative_average']['travel_time'],
                    comparison['cooperative_average']['wait_time'],
                    comparison['cooperative_average']['completed'],
                    comparison['cooperative_average']['congestion'] * 100
                ]
            })
            
            # Create grouped bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Selfish (Nash)',
                x=metrics_df['Metric'],
                y=metrics_df['Selfish'],
                marker_color='red'
            ))
            fig.add_trace(go.Bar(
                name='Cooperative (Social)',
                x=metrics_df['Metric'],
                y=metrics_df['Cooperative'],
                marker_color='green'
            ))
            
            fig.update_layout(
                barmode='group',
                title="Performance Comparison",
                xaxis_title="Metric",
                yaxis_title="Value",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show improvements
            col1, col2, col3, col4 = st.columns(4)
            improvements = comparison['improvements']
            
            with col1:
                st.metric(
                    "Travel Time",
                    f"{improvements['travel_time_improvement']:.1f}%",
                    delta=f"{improvements['travel_time_improvement']:.1f}%",
                    delta_color="inverse"
                )
            
            with col2:
                st.metric(
                    "Wait Time",
                    f"{improvements['wait_time_improvement']:.1f}%",
                    delta=f"{improvements['wait_time_improvement']:.1f}%",
                    delta_color="inverse"
                )
            
            with col3:
                st.metric(
                    "Throughput",
                    f"{improvements['throughput_improvement']:.1f}%",
                    delta=f"{improvements['throughput_improvement']:.1f}%"
                )
            
            with col4:
                st.metric(
                    "Congestion",
                    f"{improvements['congestion_improvement']:.1f}%",
                    delta=f"{improvements['congestion_improvement']:.1f}%",
                    delta_color="inverse"
                )
    
    def render_braess_paradox(self, analytics):
        """Render Braess's Paradox detection"""
        st.subheader("🔍 Braess's Paradox Detection")
        
        braess_report = analytics.get_braess_report()
        
        if braess_report['events_detected'] > 0:
            st.warning(f"⚠️ {braess_report['message']}")
            
            latest = braess_report['latest_event']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Events Detected",
                    braess_report['events_detected']
                )
            
            with col2:
                st.metric(
                    "Before Efficiency",
                    f"{latest['before_efficiency']:.4f}"
                )
            
            with col3:
                st.metric(
                    "After Efficiency",
                    f"{latest['after_efficiency']:.4f}",
                    delta=f"{(latest['efficiency_ratio'] - 1) * 100:.1f}%",
                    delta_color="inverse"
                )
        else:
            st.info("✅ No Braess's Paradox events detected")
    
    def render_network_visualization(self, env):
        """Render network graph visualization"""
        st.subheader("🗺️ Network Visualization")
        
        # Create network graph using plotly
        edge_x = []
        edge_y = []
        
        for (start, end), road in env.roads.items():
            start_pos = env.graph.nodes[start]['pos']
            end_pos = env.graph.nodes[end]['pos']
            
            edge_x.extend([start_pos[0], end_pos[0], None])
            edge_y.extend([start_pos[1], end_pos[1], None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Add nodes
        node_x = []
        node_y = []
        node_text = []
        
        for node_id in env.graph.nodes():
            pos = env.graph.nodes[node_id]['pos']
            node_x.append(pos[0])
            node_y.append(pos[1])
            node_text.append(f"Intersection {node_id}")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                size=20,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=0),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=500
                       ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_time_series(self, history: List[Dict]):
        """Render time series charts"""
        st.subheader("📉 Time Series Analysis")
        
        if not history:
            st.info("No data available yet. Start the simulation to see charts.")
            return
        
        df = pd.DataFrame(history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Wait time over time
            fig = px.line(df, x='step', y='avg_wait_time',
                         title='Average Wait Time Over Time',
                         labels={'avg_wait_time': 'Avg Wait Time (s)', 'step': 'Step'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Congestion over time
            fig = px.line(df, x='step', y='avg_congestion',
                         title='Average Congestion Over Time',
                         labels={'avg_congestion': 'Avg Congestion', 'step': 'Step'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Throughput over time
        fig = px.line(df, x='step', y='completed_vehicles',
                     title='Vehicles Completed Over Time',
                     labels={'completed_vehicles': 'Completed Vehicles', 'step': 'Step'})
        st.plotly_chart(fig, use_container_width=True)
    
    def render_info_panel(self):
        """Render information panel"""
        with st.expander("ℹ️ About This Simulation"):
            st.markdown("""
            ### Multi-Agent Traffic Simulation Platform
            
            This platform demonstrates the difference between:
            
            **Selfish Agents (Nash Equilibrium)**
            - Use greedy algorithms (Dijkstra/A*) to minimize personal travel time
            - Don't consider impact on other agents
            - Represent typical human driving behavior
            
            **Cooperative Agents (Social Optimum)**
            - Use Multi-Agent Reinforcement Learning (MARL)
            - Share global reward function
            - Optimize for system-wide throughput
            
            **Key Concepts:**
            
            - **Price of Anarchy (PoA)**: Measures efficiency loss from selfish behavior
            - **Braess's Paradox**: Adding roads can worsen congestion
            - **Game Theory**: Strategic interaction between rational decision-makers
            - **MARL**: Multiple agents learning simultaneously in shared environment
            
            **Tech Stack:**
            Python, NetworkX, Ray RLlib, PettingZoo, Streamlit, Plotly
            """)
