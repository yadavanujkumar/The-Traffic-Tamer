"""
Agents Module
Contains Selfish (Nash Equilibrium) and Cooperative (Social Optimum) agents
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


class Agent(ABC):
    """Base agent class"""
    
    def __init__(self, agent_id: int, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        
    @abstractmethod
    def plan_route(self, env, start: int, goal: int) -> List[int]:
        """Plan a route from start to goal"""
        pass
    
    @abstractmethod
    def get_action(self, env, vehicle_id: int) -> Optional[int]:
        """Get the next action for the vehicle"""
        pass


class SelfishAgent(Agent):
    """
    Selfish Agent using Nash Equilibrium strategy
    Uses greedy algorithms (Dijkstra/A*) to optimize personal travel time
    """
    
    def __init__(self, agent_id: int, algorithm: str = 'dijkstra', recalculate_frequency: int = 10):
        super().__init__(agent_id, 'selfish')
        self.algorithm = algorithm
        self.recalculate_frequency = recalculate_frequency
        self.steps_since_recalculation = {}
        
    def plan_route(self, env, start: int, goal: int) -> List[int]:
        """Plan route using Dijkstra's algorithm based on current congestion"""
        try:
            if self.algorithm == 'dijkstra':
                path = nx.dijkstra_path(env.graph, start, goal, weight='weight')
            elif self.algorithm == 'astar':
                def heuristic(u, v):
                    pos_u = env.graph.nodes[u]['pos']
                    pos_v = env.graph.nodes[v]['pos']
                    return np.sqrt((pos_u[0] - pos_v[0])**2 + (pos_u[1] - pos_v[1])**2)
                path = nx.astar_path(env.graph, start, goal, heuristic=heuristic, weight='weight')
            else:
                path = nx.shortest_path(env.graph, start, goal, weight='weight')
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [start, goal]
    
    def get_action(self, env, vehicle_id: int) -> Optional[int]:
        """Get next action for the vehicle"""
        vehicle = env.vehicles[vehicle_id]
        
        # Initialize recalculation counter
        if vehicle_id not in self.steps_since_recalculation:
            self.steps_since_recalculation[vehicle_id] = 0
        
        # Recalculate path periodically based on current congestion
        if not vehicle['path'] or self.steps_since_recalculation[vehicle_id] >= self.recalculate_frequency:
            vehicle['path'] = self.plan_route(env, vehicle['current_position'], vehicle['goal'])
            vehicle['path_index'] = 0
            self.steps_since_recalculation[vehicle_id] = 0
        
        self.steps_since_recalculation[vehicle_id] += 1
        
        # Get next position from path
        if vehicle['path_index'] < len(vehicle['path']) - 1:
            next_pos = vehicle['path'][vehicle['path_index'] + 1]
            return next_pos
        
        return None


class CooperativeAgent(Agent):
    """
    Cooperative Agent using Social Optimum strategy
    Uses Multi-Agent Reinforcement Learning to maximize system throughput
    """
    
    def __init__(self, agent_id: int, algorithm: str = 'qlearning', 
                 learning_rate: float = 0.001, discount_factor: float = 0.99,
                 epsilon_start: float = 1.0, epsilon_min: float = 0.01, 
                 epsilon_decay: float = 0.995):
        super().__init__(agent_id, 'cooperative')
        self.algorithm = algorithm
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Q-table or policy network (simplified for demonstration)
        self.q_table: Dict[Tuple, Dict[int, float]] = {}
        
    def get_state_representation(self, env, vehicle_id: int) -> Tuple:
        """Get state representation for the vehicle"""
        vehicle = env.vehicles[vehicle_id]
        current = vehicle['current_position']
        goal = vehicle['goal']
        
        # Get congestion levels of neighboring roads
        neighbors = list(env.graph.neighbors(current))
        congestion_levels = []
        for neighbor in neighbors[:4]:  # Limit to 4 neighbors for state space
            if (current, neighbor) in env.roads:
                congestion = env.roads[(current, neighbor)].get_congestion()
                congestion_levels.append(round(congestion, 1))
            else:
                congestion_levels.append(0.0)
        
        # Pad to fixed size
        while len(congestion_levels) < 4:
            congestion_levels.append(0.0)
        
        state = (current, goal, tuple(congestion_levels[:4]))
        return state
    
    def get_possible_actions(self, env, current: int) -> List[int]:
        """Get possible actions (neighboring nodes)"""
        return list(env.graph.neighbors(current))
    
    def get_q_value(self, state: Tuple, action: int) -> float:
        """Get Q-value for state-action pair"""
        if state not in self.q_table:
            self.q_table[state] = {}
        return self.q_table[state].get(action, 0.0)
    
    def update_q_value(self, state: Tuple, action: int, reward: float, next_state: Tuple):
        """Update Q-value using Q-learning"""
        if state not in self.q_table:
            self.q_table[state] = {}
        
        current_q = self.q_table[state].get(action, 0.0)
        
        # Get max Q-value for next state
        if next_state not in self.q_table:
            self.q_table[next_state] = {}
        max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def calculate_global_reward(self, env, vehicle_id: int) -> float:
        """
        Calculate reward based on global system performance
        Encourages behavior that improves overall throughput
        """
        vehicle = env.vehicles[vehicle_id]
        
        # Base reward for moving
        reward = 1.0
        
        # Penalty for congestion contribution
        current = vehicle['current_position']
        neighbors = list(env.graph.neighbors(current))
        avg_neighbor_congestion = np.mean([
            env.roads.get((current, n), env.roads.get((n, current))).get_congestion()
            for n in neighbors
            if (current, n) in env.roads or (n, current) in env.roads
        ]) if neighbors else 0.0
        
        # Reward for choosing less congested paths
        reward -= avg_neighbor_congestion * 2.0
        
        # Bonus for completing journey
        if vehicle['completed']:
            reward += 10.0
        
        # Global system reward component
        metrics = env._collect_metrics()
        system_efficiency = metrics['completed_vehicles'] / max(1, metrics['active_vehicles'] + metrics['completed_vehicles'])
        reward += system_efficiency * 5.0
        
        return reward
    
    def plan_route(self, env, start: int, goal: int) -> List[int]:
        """Plan route using learned policy"""
        path = [start]
        current = start
        max_steps = 50  # Prevent infinite loops
        steps = 0
        
        while current != goal and steps < max_steps:
            state = self.get_state_representation(env, env.vehicles.get(self.agent_id, {'current_position': current, 'goal': goal}))
            actions = self.get_possible_actions(env, current)
            
            if not actions:
                break
            
            # Epsilon-greedy action selection
            if np.random.random() < self.epsilon:
                # Explore: choose random action
                action = np.random.choice(actions)
            else:
                # Exploit: choose best action
                q_values = [self.get_q_value(state, a) for a in actions]
                best_action_idx = np.argmax(q_values)
                action = actions[best_action_idx]
            
            path.append(action)
            current = action
            steps += 1
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return path
    
    def get_action(self, env, vehicle_id: int) -> Optional[int]:
        """Get next action for the vehicle"""
        vehicle = env.vehicles[vehicle_id]
        
        # Plan or replan route
        if not vehicle['path']:
            vehicle['path'] = self.plan_route(env, vehicle['current_position'], vehicle['goal'])
            vehicle['path_index'] = 0
        
        # Get next position from path
        if vehicle['path_index'] < len(vehicle['path']) - 1:
            next_pos = vehicle['path'][vehicle['path_index'] + 1]
            
            # Update Q-values based on reward
            state = self.get_state_representation(env, vehicle_id)
            reward = self.calculate_global_reward(env, vehicle_id)
            next_state = self.get_state_representation(env, vehicle_id)
            self.update_q_value(state, next_pos, reward, next_state)
            
            return next_pos
        
        return None


class AgentManager:
    """Manages all agents in the simulation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        
    def create_agent(self, agent_type: str) -> Agent:
        """Create a new agent"""
        agent_id = self.next_agent_id
        self.next_agent_id += 1
        
        if agent_type == 'selfish':
            selfish_config = self.config['agents']['selfish']
            agent = SelfishAgent(
                agent_id,
                algorithm=selfish_config['algorithm'],
                recalculate_frequency=selfish_config['recalculate_frequency']
            )
        elif agent_type == 'cooperative':
            coop_config = self.config['agents']['cooperative']
            agent = CooperativeAgent(
                agent_id,
                algorithm=coop_config['algorithm'],
                learning_rate=coop_config['learning_rate'],
                discount_factor=coop_config['discount_factor'],
                epsilon_start=coop_config['epsilon_start'],
                epsilon_min=coop_config['epsilon_min'],
                epsilon_decay=coop_config['epsilon_decay']
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        self.agents[agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
