"""
Test Suite for Traffic Tamer
Tests core functionality without requiring GUI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import yaml
import numpy as np
from traffic_tamer.environment import TrafficEnvironment, TrafficLight, Road, TrafficLightState
from traffic_tamer.agents import AgentManager, SelfishAgent, CooperativeAgent
from traffic_tamer.analytics import Analytics


class TestTrafficEnvironment(unittest.TestCase):
    """Test the traffic environment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'simulation': {
                'grid_width': 10,
                'grid_height': 10,
                'num_intersections': 16,
                'road_capacity': 10,
                'base_speed': 5.0,
                'max_steps': 1000,
                'num_vehicles': 50,
                'spawn_rate': 0.1,
                'traffic_light_cycle': 30,
                'green_duration': 15,
                'yellow_duration': 3
            },
            'agents': {
                'selfish': {
                    'strategy': 'nash',
                    'algorithm': 'dijkstra',
                    'recalculate_frequency': 10
                },
                'cooperative': {
                    'strategy': 'social',
                    'algorithm': 'qlearning',
                    'learning_rate': 0.001,
                    'discount_factor': 0.99,
                    'epsilon_start': 1.0,
                    'epsilon_min': 0.01,
                    'epsilon_decay': 0.995
                }
            },
            'analytics': {
                'calculate_poa': True,
                'poa_window': 100,
                'detect_braess': True,
                'braess_threshold': 1.1,
                'track_wait_time': True,
                'track_fuel_consumption': True,
                'track_throughput': True
            }
        }
        self.env = TrafficEnvironment(self.config)
    
    def test_environment_initialization(self):
        """Test that environment initializes correctly"""
        self.assertEqual(self.env.num_intersections, 16)
        self.assertEqual(len(self.env.graph.nodes), 16)
        self.assertGreater(len(self.env.roads), 0)
        self.assertEqual(len(self.env.traffic_lights), 16)
    
    def test_traffic_light_cycle(self):
        """Test traffic light state transitions"""
        light = TrafficLight(cycle_time=30, green_duration=15, yellow_duration=3)
        
        # Should start green
        self.assertEqual(light.state, TrafficLightState.GREEN)
        
        # Step through cycle
        for _ in range(15):
            light.step()
        self.assertEqual(light.state, TrafficLightState.YELLOW)
        
        for _ in range(3):
            light.step()
        self.assertEqual(light.state, TrafficLightState.RED)
    
    def test_road_congestion(self):
        """Test road congestion calculation"""
        road = Road(0, 1, capacity=10)
        
        # Empty road
        self.assertEqual(road.get_congestion(), 0.0)
        
        # Add vehicles
        for i in range(5):
            road.add_vehicle(i)
        self.assertEqual(road.get_congestion(), 0.5)
        
        # Full capacity
        for i in range(5, 10):
            road.add_vehicle(i)
        self.assertEqual(road.get_congestion(), 1.0)
    
    def test_vehicle_spawning(self):
        """Test vehicle spawning"""
        vehicle_id = self.env.spawn_vehicle(start=0, goal=15, agent_type='selfish')
        
        self.assertIn(vehicle_id, self.env.vehicles)
        vehicle = self.env.vehicles[vehicle_id]
        self.assertEqual(vehicle['start'], 0)
        self.assertEqual(vehicle['goal'], 15)
        self.assertEqual(vehicle['agent_type'], 'selfish')
        self.assertFalse(vehicle['completed'])
    
    def test_environment_step(self):
        """Test environment step function"""
        metrics = self.env.step()
        
        self.assertIn('step', metrics)
        self.assertIn('active_vehicles', metrics)
        self.assertIn('avg_congestion', metrics)
        self.assertEqual(metrics['step'], 1)
    
    def test_graph_connectivity(self):
        """Test that graph is properly connected"""
        import networkx as nx
        
        # Check if graph is connected (undirected version)
        undirected = self.env.graph.to_undirected()
        self.assertTrue(nx.is_connected(undirected))


class TestAgents(unittest.TestCase):
    """Test agent behavior"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'simulation': {
                'grid_width': 10,
                'grid_height': 10,
                'num_intersections': 16,
                'road_capacity': 10,
                'base_speed': 5.0,
                'max_steps': 1000,
                'num_vehicles': 50,
                'spawn_rate': 0.1,
                'traffic_light_cycle': 30,
                'green_duration': 15,
                'yellow_duration': 3
            },
            'agents': {
                'selfish': {
                    'strategy': 'nash',
                    'algorithm': 'dijkstra',
                    'recalculate_frequency': 10
                },
                'cooperative': {
                    'strategy': 'social',
                    'algorithm': 'qlearning',
                    'learning_rate': 0.001,
                    'discount_factor': 0.99,
                    'epsilon_start': 1.0,
                    'epsilon_min': 0.01,
                    'epsilon_decay': 0.995
                }
            },
            'analytics': {
                'calculate_poa': True,
                'poa_window': 100,
                'detect_braess': True,
                'braess_threshold': 1.1,
                'track_wait_time': True,
                'track_fuel_consumption': True,
                'track_throughput': True
            }
        }
        self.env = TrafficEnvironment(self.config)
        self.agent_manager = AgentManager(self.config)
    
    def test_selfish_agent_creation(self):
        """Test selfish agent creation"""
        agent = self.agent_manager.create_agent('selfish')
        
        self.assertIsInstance(agent, SelfishAgent)
        self.assertEqual(agent.agent_type, 'selfish')
    
    def test_cooperative_agent_creation(self):
        """Test cooperative agent creation"""
        agent = self.agent_manager.create_agent('cooperative')
        
        self.assertIsInstance(agent, CooperativeAgent)
        self.assertEqual(agent.agent_type, 'cooperative')
    
    def test_selfish_agent_pathfinding(self):
        """Test selfish agent can find paths"""
        agent = self.agent_manager.create_agent('selfish')
        path = agent.plan_route(self.env, 0, 15)
        
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 15)
    
    def test_cooperative_agent_pathfinding(self):
        """Test cooperative agent can find paths"""
        agent = self.agent_manager.create_agent('cooperative')
        path = agent.plan_route(self.env, 0, 15)
        
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
    
    def test_agent_get_action(self):
        """Test agent action generation"""
        agent = self.agent_manager.create_agent('selfish')
        vehicle_id = self.env.spawn_vehicle(start=0, goal=15, agent_type='selfish')
        
        action = agent.get_action(self.env, vehicle_id)
        
        # Should return a valid neighboring node or None
        if action is not None:
            self.assertIn(action, self.env.graph.neighbors(0))


class TestAnalytics(unittest.TestCase):
    """Test analytics engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'analytics': {
                'calculate_poa': True,
                'poa_window': 100,
                'detect_braess': True,
                'braess_threshold': 1.1,
                'track_wait_time': True,
                'track_fuel_consumption': True,
                'track_throughput': True
            }
        }
        self.analytics = Analytics(self.config)
    
    def test_analytics_initialization(self):
        """Test analytics initialization"""
        self.assertEqual(self.analytics.poa_window, 100)
        self.assertEqual(self.analytics.braess_threshold, 1.1)
        self.assertEqual(self.analytics.current_poa, 1.0)
    
    def test_record_metrics(self):
        """Test metrics recording"""
        metrics = {
            'step': 1,
            'active_vehicles': 10,
            'completed_vehicles': 5,
            'total_wait_time': 100,
            'total_travel_time': 200,
            'avg_congestion': 0.5,
            'avg_wait_time': 10,
            'avg_travel_time': 40
        }
        
        self.analytics.record_metrics(metrics, 'selfish')
        self.assertEqual(len(self.analytics.selfish_metrics_history), 1)
    
    def test_price_of_anarchy_calculation(self):
        """Test Price of Anarchy calculation"""
        # Record metrics for both types
        selfish_metrics = {
            'step': 1,
            'active_vehicles': 10,
            'completed_vehicles': 5,
            'total_wait_time': 150,
            'total_travel_time': 300,
            'avg_congestion': 0.7,
            'avg_wait_time': 15,
            'avg_travel_time': 60
        }
        
        cooperative_metrics = {
            'step': 1,
            'active_vehicles': 10,
            'completed_vehicles': 8,
            'total_wait_time': 80,
            'total_travel_time': 200,
            'avg_congestion': 0.4,
            'avg_wait_time': 8,
            'avg_travel_time': 25
        }
        
        self.analytics.record_metrics(selfish_metrics, 'selfish')
        self.analytics.record_metrics(cooperative_metrics, 'cooperative')
        
        poa = self.analytics.calculate_price_of_anarchy()
        
        # PoA should be > 1 since selfish has worse performance
        self.assertGreater(poa, 1.0)
    
    def test_braess_paradox_detection(self):
        """Test Braess's Paradox detection"""
        before_metrics = {
            'step': 1,
            'active_vehicles': 10,
            'completed_vehicles': 10,
            'total_wait_time': 100,
            'total_travel_time': 200,
            'avg_congestion': 0.5,
            'avg_wait_time': 10,
            'avg_travel_time': 20
        }
        
        # After metrics show decreased efficiency
        after_metrics = {
            'step': 2,
            'active_vehicles': 10,
            'completed_vehicles': 5,  # Fewer completed
            'total_wait_time': 200,  # More wait time
            'total_travel_time': 400,  # More travel time
            'avg_congestion': 0.8,
            'avg_wait_time': 20,
            'avg_travel_time': 80
        }
        
        detected = self.analytics.detect_braess_paradox(
            before_metrics, after_metrics, (0, 1)
        )
        
        self.assertTrue(detected)
        self.assertTrue(self.analytics.braess_detected)
        self.assertEqual(len(self.analytics.braess_events), 1)
    
    def test_system_performance_summary(self):
        """Test system performance summary"""
        summary = self.analytics.get_system_performance_summary()
        
        self.assertIn('current_poa', summary)
        self.assertIn('avg_poa', summary)
        self.assertIn('braess_events_count', summary)
        self.assertIn('braess_detected', summary)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'simulation': {
                'grid_width': 10,
                'grid_height': 10,
                'num_intersections': 16,
                'road_capacity': 10,
                'base_speed': 5.0,
                'max_steps': 1000,
                'num_vehicles': 10,
                'spawn_rate': 0.1,
                'traffic_light_cycle': 30,
                'green_duration': 15,
                'yellow_duration': 3
            },
            'agents': {
                'selfish': {
                    'strategy': 'nash',
                    'algorithm': 'dijkstra',
                    'recalculate_frequency': 10
                },
                'cooperative': {
                    'strategy': 'social',
                    'algorithm': 'qlearning',
                    'learning_rate': 0.001,
                    'discount_factor': 0.99,
                    'epsilon_start': 1.0,
                    'epsilon_min': 0.01,
                    'epsilon_decay': 0.995
                }
            },
            'analytics': {
                'calculate_poa': True,
                'poa_window': 100,
                'detect_braess': True,
                'braess_threshold': 1.1,
                'track_wait_time': True,
                'track_fuel_consumption': True,
                'track_throughput': True
            }
        }
    
    def test_complete_simulation_run(self):
        """Test a complete simulation run"""
        env = TrafficEnvironment(self.config)
        agent_manager = AgentManager(self.config)
        analytics = Analytics(self.config)
        
        # Spawn vehicles
        for i in range(5):
            agent = agent_manager.create_agent('selfish')
            vehicle_id = env.spawn_vehicle(agent_type='selfish')
        
        # Run simulation
        for step in range(50):
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
            
            analytics.record_metrics(metrics, 'selfish')
        
        # Check that simulation ran
        final_metrics = env._collect_metrics()
        self.assertGreaterEqual(final_metrics['step'], 50)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTrafficEnvironment))
    suite.addTests(loader.loadTestsFromTestCase(TestAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
