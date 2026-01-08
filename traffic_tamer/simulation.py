"""
Simulation Controller
Main controller for running traffic simulations
"""

import yaml
import numpy as np
from typing import Dict, List, Optional
from traffic_tamer.environment import TrafficEnvironment
from traffic_tamer.agents import AgentManager, SelfishAgent, CooperativeAgent
from traffic_tamer.analytics import Analytics
from traffic_tamer.visualization import PygameVisualizer


class SimulationController:
    """Main simulation controller"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.env = TrafficEnvironment(self.config)
        self.agent_manager = AgentManager(self.config)
        self.analytics = Analytics(self.config)
        
        # Visualization
        self.visualizer = None
        if self.config['visualization']['mode'] == 'pygame':
            self.visualizer = PygameVisualizer(self.config)
        
        # Simulation state
        self.running = False
        self.current_episode = 0
        self.metrics_history = []
        
    def setup_simulation(self, agent_type: str = 'mixed', num_vehicles: Optional[int] = None):
        """Setup simulation with agents"""
        if num_vehicles is None:
            num_vehicles = self.config['simulation']['num_vehicles']
        
        # Reset environment
        self.env.reset()
        
        # Create agents and spawn vehicles
        if agent_type == 'selfish':
            # All selfish agents
            for _ in range(num_vehicles):
                agent = self.agent_manager.create_agent('selfish')
                vehicle_id = self.env.spawn_vehicle(agent_type='selfish')
        elif agent_type == 'cooperative':
            # All cooperative agents
            for _ in range(num_vehicles):
                agent = self.agent_manager.create_agent('cooperative')
                vehicle_id = self.env.spawn_vehicle(agent_type='cooperative')
        else:  # mixed
            # Half selfish, half cooperative
            for i in range(num_vehicles):
                if i < num_vehicles // 2:
                    agent = self.agent_manager.create_agent('selfish')
                    vehicle_id = self.env.spawn_vehicle(agent_type='selfish')
                else:
                    agent = self.agent_manager.create_agent('cooperative')
                    vehicle_id = self.env.spawn_vehicle(agent_type='cooperative')
    
    def run_episode(self, agent_type: str = 'mixed', render: bool = True) -> Dict:
        """Run a single episode"""
        self.setup_simulation(agent_type)
        
        max_steps = self.config['simulation']['max_steps']
        
        for step in range(max_steps):
            # Update environment
            metrics = self.env.step()
            
            # Move vehicles
            for vehicle_id, vehicle in list(self.env.vehicles.items()):
                if vehicle['completed']:
                    continue
                
                # Get agent for this vehicle
                agent = None
                for a in self.agent_manager.agents.values():
                    if a.agent_type == vehicle['agent_type']:
                        agent = a
                        break
                
                if agent:
                    next_pos = agent.get_action(self.env, vehicle_id)
                    if next_pos is not None:
                        self.env.move_vehicle(vehicle_id, next_pos)
            
            # Record metrics
            self.metrics_history.append(metrics)
            self.analytics.record_metrics(metrics, agent_type)
            
            # Render
            if render and self.visualizer:
                if not self.visualizer.handle_events():
                    break
                self.visualizer.render(self.env, self.analytics)
            
            # Check if all vehicles completed
            if metrics['active_vehicles'] == 0:
                break
        
        # Calculate analytics
        poa = self.analytics.calculate_price_of_anarchy()
        
        return metrics
    
    def run_comparison(self, num_episodes: int = 10) -> Dict:
        """Run comparison between selfish and cooperative strategies"""
        print(f"Running {num_episodes} episodes for each strategy...")
        
        # Run selfish episodes
        print("\nRunning selfish (Nash Equilibrium) strategy...")
        selfish_results = []
        for ep in range(num_episodes):
            print(f"  Episode {ep + 1}/{num_episodes}")
            result = self.run_episode('selfish', render=False)
            selfish_results.append(result)
        
        # Run cooperative episodes
        print("\nRunning cooperative (Social Optimum) strategy...")
        cooperative_results = []
        for ep in range(num_episodes):
            print(f"  Episode {ep + 1}/{num_episodes}")
            result = self.run_episode('cooperative', render=False)
            cooperative_results.append(result)
        
        # Get comparative analysis
        analysis = self.analytics.get_comparative_analysis()
        
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        
        if analysis:
            print(f"\nSelfish (Nash Equilibrium) Average:")
            print(f"  Travel Time: {analysis['selfish_average']['travel_time']:.2f}s")
            print(f"  Wait Time: {analysis['selfish_average']['wait_time']:.2f}s")
            print(f"  Completed: {analysis['selfish_average']['completed']:.1f} vehicles")
            print(f"  Congestion: {analysis['selfish_average']['congestion']:.1%}")
            
            print(f"\nCooperative (Social Optimum) Average:")
            print(f"  Travel Time: {analysis['cooperative_average']['travel_time']:.2f}s")
            print(f"  Wait Time: {analysis['cooperative_average']['wait_time']:.2f}s")
            print(f"  Completed: {analysis['cooperative_average']['completed']:.1f} vehicles")
            print(f"  Congestion: {analysis['cooperative_average']['congestion']:.1%}")
            
            print(f"\nImprovements (Cooperative vs Selfish):")
            print(f"  Travel Time: {analysis['improvements']['travel_time_improvement']:.1f}%")
            print(f"  Wait Time: {analysis['improvements']['wait_time_improvement']:.1f}%")
            print(f"  Throughput: {analysis['improvements']['throughput_improvement']:.1f}%")
            print(f"  Congestion: {analysis['improvements']['congestion_improvement']:.1f}%")
            
            print(f"\nPrice of Anarchy: {self.analytics.current_poa:.3f}")
            print(f"Winner: {analysis['winner'].upper()}")
        
        print("="*60)
        
        return analysis
    
    def run_interactive(self):
        """Run interactive simulation with visualization"""
        print("Starting interactive simulation...")
        print("Press ESC or close window to exit")
        
        self.setup_simulation('mixed')
        self.running = True
        
        while self.running:
            # Update
            metrics = self.env.step()
            
            # Move vehicles
            for vehicle_id, vehicle in list(self.env.vehicles.items()):
                if vehicle['completed']:
                    continue
                
                # Get agent
                agent = None
                for a in self.agent_manager.agents.values():
                    if a.agent_type == vehicle['agent_type']:
                        agent = a
                        break
                
                if agent:
                    next_pos = agent.get_action(self.env, vehicle_id)
                    if next_pos is not None:
                        self.env.move_vehicle(vehicle_id, next_pos)
            
            # Record metrics
            self.analytics.record_metrics(metrics, 'mixed')
            
            # Render
            if self.visualizer:
                if not self.visualizer.handle_events():
                    self.running = False
                self.visualizer.render(self.env, self.analytics)
            
            # Respawn vehicles
            if len(self.env.vehicles) < self.config['simulation']['num_vehicles']:
                if np.random.random() < self.config['simulation']['spawn_rate']:
                    agent_type = 'selfish' if np.random.random() < 0.5 else 'cooperative'
                    agent = self.agent_manager.create_agent(agent_type)
                    self.env.spawn_vehicle(agent_type=agent_type)
        
        if self.visualizer:
            self.visualizer.close()
    
    def close(self):
        """Clean up resources"""
        if self.visualizer:
            self.visualizer.close()
