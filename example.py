#!/usr/bin/env python3
"""
Quick Start Example
Demonstrates basic usage of the Traffic Tamer simulation
"""

import yaml
from traffic_tamer.environment import TrafficEnvironment
from traffic_tamer.agents import AgentManager
from traffic_tamer.analytics import Analytics


def simple_example():
    """Run a simple example simulation"""
    print("=" * 60)
    print("Traffic Tamer - Quick Start Example")
    print("=" * 60)
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create environment
    print("\n1. Creating traffic environment...")
    env = TrafficEnvironment(config)
    print(f"   Created {env.num_intersections} intersection grid")
    print(f"   Total roads: {len(env.roads)}")
    
    # Create agent manager
    print("\n2. Creating agents...")
    agent_manager = AgentManager(config)
    
    # Create some agents
    selfish_agent = agent_manager.create_agent('selfish')
    cooperative_agent = agent_manager.create_agent('cooperative')
    print(f"   Created 2 agents (1 selfish, 1 cooperative)")
    
    # Spawn vehicles
    print("\n3. Spawning vehicles...")
    vehicle1 = env.spawn_vehicle(start=0, goal=15, agent_type='selfish')
    vehicle2 = env.spawn_vehicle(start=3, goal=12, agent_type='cooperative')
    print(f"   Spawned 2 vehicles")
    
    # Run simulation for a few steps
    print("\n4. Running simulation...")
    for step in range(20):
        # Update environment
        metrics = env.step()
        
        # Move vehicles
        for vehicle_id, vehicle in env.vehicles.items():
            if vehicle['completed']:
                continue
            
            # Get appropriate agent
            agent = selfish_agent if vehicle['agent_type'] == 'selfish' else cooperative_agent
            
            # Get next action
            next_pos = agent.get_action(env, vehicle_id)
            if next_pos is not None:
                success = env.move_vehicle(vehicle_id, next_pos)
                if success:
                    print(f"   Step {step}: Vehicle {vehicle_id} ({vehicle['agent_type']}) "
                          f"moved to {next_pos}")
        
        # Check if all vehicles completed
        if all(v['completed'] for v in env.vehicles.values()):
            print(f"\n   All vehicles completed in {step + 1} steps!")
            break
    
    # Show final metrics
    print("\n5. Final Metrics:")
    final_metrics = env._collect_metrics()
    print(f"   Total Wait Time: {final_metrics['total_wait_time']:.2f}s")
    print(f"   Total Travel Time: {final_metrics['total_travel_time']:.2f}s")
    print(f"   Vehicles Completed: {final_metrics['completed_vehicles']}")
    print(f"   Average Congestion: {final_metrics['avg_congestion']:.1%}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("\nNext steps:")
    print("  - Run 'python main.py --mode comparison' for full comparison")
    print("  - Run 'python main.py --mode pygame' for visualization")
    print("  - Run 'streamlit run app_streamlit.py' for web dashboard")
    print("=" * 60)


if __name__ == '__main__':
    simple_example()
