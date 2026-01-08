"""
Environment Module
Contains the traffic simulation environment with intersections, roads, and traffic lights
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from enum import Enum


class TrafficLightState(Enum):
    """Traffic light states"""
    RED = 0
    YELLOW = 1
    GREEN = 2


class TrafficLight:
    """Traffic light at an intersection"""
    
    def __init__(self, cycle_time: int = 30, green_duration: int = 15, yellow_duration: int = 3):
        self.cycle_time = cycle_time
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.red_duration = cycle_time - green_duration - yellow_duration
        self.current_time = 0
        self.state = TrafficLightState.GREEN
        
    def step(self):
        """Update traffic light state"""
        self.current_time += 1
        
        if self.current_time < self.green_duration:
            self.state = TrafficLightState.GREEN
        elif self.current_time < self.green_duration + self.yellow_duration:
            self.state = TrafficLightState.YELLOW
        elif self.current_time < self.cycle_time:
            self.state = TrafficLightState.RED
        else:
            self.current_time = 0
            self.state = TrafficLightState.GREEN
            
        return self.state
    
    def can_pass(self) -> bool:
        """Check if vehicles can pass through the intersection"""
        return self.state == TrafficLightState.GREEN


class Road:
    """Road segment connecting two intersections"""
    
    def __init__(self, start: int, end: int, capacity: int = 10, length: float = 1.0):
        self.start = start
        self.end = end
        self.capacity = capacity
        self.length = length
        self.vehicles = []
        
    def add_vehicle(self, vehicle_id: int) -> bool:
        """Add a vehicle to the road"""
        if len(self.vehicles) < self.capacity:
            self.vehicles.append(vehicle_id)
            return True
        return False
    
    def remove_vehicle(self, vehicle_id: int):
        """Remove a vehicle from the road"""
        if vehicle_id in self.vehicles:
            self.vehicles.remove(vehicle_id)
    
    def get_congestion(self) -> float:
        """Get congestion level (0.0 to 1.0)"""
        return len(self.vehicles) / self.capacity if self.capacity > 0 else 1.0
    
    def get_travel_time(self, base_speed: float = 5.0) -> float:
        """Calculate travel time based on congestion"""
        congestion = self.get_congestion()
        # BPR (Bureau of Public Roads) function for travel time
        return self.length / base_speed * (1 + 0.15 * (congestion ** 4))


class TrafficEnvironment:
    """Main traffic simulation environment"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.grid_width = config['simulation']['grid_width']
        self.grid_height = config['simulation']['grid_height']
        self.num_intersections = config['simulation']['num_intersections']
        self.road_capacity = config['simulation']['road_capacity']
        self.base_speed = config['simulation']['base_speed']
        self.max_steps = config['simulation']['max_steps']
        
        # Initialize graph structure
        self.graph = nx.DiGraph()
        self.roads: Dict[Tuple[int, int], Road] = {}
        self.traffic_lights: Dict[int, TrafficLight] = {}
        self.vehicles: Dict[int, Dict] = {}
        self.next_vehicle_id = 0
        
        # Metrics
        self.current_step = 0
        self.total_wait_time = 0
        self.total_travel_time = 0
        self.vehicles_completed = 0
        
        # Build the environment
        self._build_grid()
        self._setup_traffic_lights()
        
    def _build_grid(self):
        """Build the traffic grid network"""
        # Create intersections as nodes
        for i in range(self.num_intersections):
            self.graph.add_node(i, pos=self._get_intersection_position(i))
        
        # Create roads as edges (grid pattern)
        nodes_per_row = int(np.sqrt(self.num_intersections))
        for i in range(self.num_intersections):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            # Connect to right neighbor
            if col < nodes_per_row - 1:
                right = i + 1
                self._add_road(i, right)
                self._add_road(right, i)  # Bidirectional
            
            # Connect to bottom neighbor
            if row < nodes_per_row - 1:
                bottom = i + nodes_per_row
                self._add_road(i, bottom)
                self._add_road(bottom, i)  # Bidirectional
    
    def _add_road(self, start: int, end: int):
        """Add a road between two intersections"""
        road = Road(start, end, capacity=self.road_capacity)
        self.roads[(start, end)] = road
        length = road.get_travel_time(self.base_speed)
        self.graph.add_edge(start, end, weight=length, road=road)
    
    def _get_intersection_position(self, node_id: int) -> Tuple[int, int]:
        """Get the grid position of an intersection"""
        nodes_per_row = int(np.sqrt(self.num_intersections))
        row = node_id // nodes_per_row
        col = node_id % nodes_per_row
        return (col, row)
    
    def _setup_traffic_lights(self):
        """Setup traffic lights at intersections"""
        cycle_time = self.config['simulation']['traffic_light_cycle']
        green_duration = self.config['simulation']['green_duration']
        yellow_duration = self.config['simulation']['yellow_duration']
        
        for i in range(self.num_intersections):
            # Offset traffic lights to create waves
            light = TrafficLight(cycle_time, green_duration, yellow_duration)
            light.current_time = i % cycle_time
            self.traffic_lights[i] = light
    
    def spawn_vehicle(self, start: Optional[int] = None, goal: Optional[int] = None, 
                     agent_type: str = 'selfish') -> int:
        """Spawn a new vehicle in the environment"""
        if start is None:
            start = np.random.randint(0, self.num_intersections)
        if goal is None:
            goal = np.random.randint(0, self.num_intersections)
            while goal == start:
                goal = np.random.randint(0, self.num_intersections)
        
        vehicle_id = self.next_vehicle_id
        self.next_vehicle_id += 1
        
        self.vehicles[vehicle_id] = {
            'id': vehicle_id,
            'start': start,
            'goal': goal,
            'current_position': start,
            'path': [],
            'path_index': 0,
            'agent_type': agent_type,
            'total_travel_time': 0,
            'total_wait_time': 0,
            'completed': False
        }
        
        return vehicle_id
    
    def get_current_edge_weights(self) -> Dict[Tuple[int, int], float]:
        """Get current edge weights based on congestion"""
        weights = {}
        for (start, end), road in self.roads.items():
            travel_time = road.get_travel_time(self.base_speed)
            weights[(start, end)] = travel_time
        return weights
    
    def update_graph_weights(self):
        """Update graph edge weights based on current congestion"""
        for (start, end), road in self.roads.items():
            travel_time = road.get_travel_time(self.base_speed)
            self.graph[start][end]['weight'] = travel_time
    
    def step(self) -> Dict:
        """Execute one simulation step"""
        self.current_step += 1
        
        # Update traffic lights
        for light in self.traffic_lights.values():
            light.step()
        
        # Update graph weights based on congestion
        self.update_graph_weights()
        
        # Collect metrics
        metrics = self._collect_metrics()
        
        return metrics
    
    def move_vehicle(self, vehicle_id: int, next_position: int) -> bool:
        """Move a vehicle to the next position"""
        vehicle = self.vehicles[vehicle_id]
        current = vehicle['current_position']
        
        # Check if road exists and has capacity
        if (current, next_position) not in self.roads:
            return False
        
        road = self.roads[(current, next_position)]
        
        # Check traffic light at the next intersection
        if not self.traffic_lights[next_position].can_pass():
            vehicle['total_wait_time'] += 1
            self.total_wait_time += 1
            return False
        
        # Try to add vehicle to road
        if road.add_vehicle(vehicle_id):
            # Remove from previous road if exists
            if current != vehicle['start']:
                prev_pos = vehicle['path'][vehicle['path_index'] - 1] if vehicle['path_index'] > 0 else vehicle['start']
                if (prev_pos, current) in self.roads:
                    self.roads[(prev_pos, current)].remove_vehicle(vehicle_id)
            
            vehicle['current_position'] = next_position
            vehicle['path_index'] += 1
            vehicle['total_travel_time'] += road.get_travel_time(self.base_speed)
            self.total_travel_time += road.get_travel_time(self.base_speed)
            
            # Check if reached goal
            if next_position == vehicle['goal']:
                vehicle['completed'] = True
                self.vehicles_completed += 1
                road.remove_vehicle(vehicle_id)
            
            return True
        else:
            vehicle['total_wait_time'] += 1
            self.total_wait_time += 1
            return False
    
    def _collect_metrics(self) -> Dict:
        """Collect current metrics"""
        active_vehicles = len([v for v in self.vehicles.values() if not v['completed']])
        avg_congestion = np.mean([road.get_congestion() for road in self.roads.values()])
        
        metrics = {
            'step': self.current_step,
            'active_vehicles': active_vehicles,
            'completed_vehicles': self.vehicles_completed,
            'total_wait_time': self.total_wait_time,
            'total_travel_time': self.total_travel_time,
            'avg_congestion': avg_congestion,
            'avg_wait_time': self.total_wait_time / max(1, len(self.vehicles)),
            'avg_travel_time': self.total_travel_time / max(1, self.vehicles_completed)
        }
        
        return metrics
    
    def reset(self):
        """Reset the environment"""
        self.vehicles = {}
        self.next_vehicle_id = 0
        self.current_step = 0
        self.total_wait_time = 0
        self.total_travel_time = 0
        self.vehicles_completed = 0
        
        # Clear roads
        for road in self.roads.values():
            road.vehicles = []
        
        # Reset traffic lights
        for i, light in enumerate(self.traffic_lights.items()):
            light[1].current_time = i % light[1].cycle_time
    
    def get_state(self) -> Dict:
        """Get current environment state"""
        return {
            'graph': self.graph,
            'roads': self.roads,
            'vehicles': self.vehicles,
            'traffic_lights': self.traffic_lights,
            'metrics': self._collect_metrics()
        }
