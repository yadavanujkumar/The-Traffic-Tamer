"""
Analytics Module
Calculates Price of Anarchy and detects Braess's Paradox
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque


class Analytics:
    """
    Analytics engine for traffic simulation
    Calculates Price of Anarchy and detects Braess's Paradox
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.poa_window = config['analytics']['poa_window']
        self.braess_threshold = config['analytics']['braess_threshold']
        
        # Historical data
        self.selfish_metrics_history: deque = deque(maxlen=self.poa_window)
        self.cooperative_metrics_history: deque = deque(maxlen=self.poa_window)
        self.poa_history: List[float] = []
        self.braess_events: List[Dict] = []
        
        # Current metrics
        self.current_poa = 1.0
        self.braess_detected = False
        
    def record_metrics(self, metrics: Dict, agent_type: str):
        """Record metrics for a simulation run"""
        if agent_type == 'selfish':
            self.selfish_metrics_history.append(metrics)
        elif agent_type == 'cooperative':
            self.cooperative_metrics_history.append(metrics)
    
    def calculate_price_of_anarchy(self) -> float:
        """
        Calculate Price of Anarchy (PoA)
        PoA = (Total cost in Nash Equilibrium) / (Total cost in Social Optimum)
        
        A PoA > 1 indicates inefficiency from selfish behavior
        """
        if not self.selfish_metrics_history or not self.cooperative_metrics_history:
            return 1.0
        
        # Calculate average metrics for selfish agents (Nash Equilibrium)
        selfish_avg_travel_time = np.mean([m['avg_travel_time'] for m in self.selfish_metrics_history])
        selfish_avg_wait_time = np.mean([m['avg_wait_time'] for m in self.selfish_metrics_history])
        selfish_total_cost = selfish_avg_travel_time + selfish_avg_wait_time
        
        # Calculate average metrics for cooperative agents (Social Optimum)
        coop_avg_travel_time = np.mean([m['avg_travel_time'] for m in self.cooperative_metrics_history])
        coop_avg_wait_time = np.mean([m['avg_wait_time'] for m in self.cooperative_metrics_history])
        coop_total_cost = coop_avg_travel_time + coop_avg_wait_time
        
        # Calculate PoA
        if coop_total_cost > 0:
            poa = selfish_total_cost / coop_total_cost
        else:
            poa = 1.0
        
        self.current_poa = poa
        self.poa_history.append(poa)
        
        return poa
    
    def detect_braess_paradox(self, before_metrics: Dict, after_metrics: Dict, 
                              road_added: Tuple[int, int]) -> bool:
        """
        Detect Braess's Paradox
        Returns True if adding a road decreased system efficiency
        
        Braess's Paradox occurs when adding capacity to a network
        actually increases congestion and travel times
        """
        before_efficiency = self._calculate_system_efficiency(before_metrics)
        after_efficiency = self._calculate_system_efficiency(after_metrics)
        
        # Check if efficiency decreased by more than threshold
        if after_efficiency < before_efficiency / self.braess_threshold:
            self.braess_detected = True
            event = {
                'road_added': road_added,
                'before_efficiency': before_efficiency,
                'after_efficiency': after_efficiency,
                'efficiency_ratio': after_efficiency / before_efficiency if before_efficiency > 0 else 0,
                'timestamp': len(self.braess_events)
            }
            self.braess_events.append(event)
            return True
        
        return False
    
    def _calculate_system_efficiency(self, metrics: Dict) -> float:
        """
        Calculate system efficiency
        Higher is better
        """
        if metrics['total_travel_time'] + metrics['total_wait_time'] == 0:
            return 0.0
        
        # Efficiency = throughput / total time
        throughput = metrics['completed_vehicles']
        total_time = metrics['total_travel_time'] + metrics['total_wait_time']
        
        efficiency = throughput / total_time
        return efficiency
    
    def get_system_performance_summary(self) -> Dict:
        """Get summary of system performance"""
        summary = {
            'current_poa': self.current_poa,
            'avg_poa': np.mean(self.poa_history) if self.poa_history else 1.0,
            'braess_events_count': len(self.braess_events),
            'braess_detected': self.braess_detected,
            'poa_trend': self._calculate_trend(self.poa_history) if len(self.poa_history) > 1 else 0.0
        }
        
        # Add detailed metrics if available
        if self.selfish_metrics_history:
            latest_selfish = list(self.selfish_metrics_history)[-1]
            summary['selfish_metrics'] = {
                'avg_travel_time': latest_selfish['avg_travel_time'],
                'avg_wait_time': latest_selfish['avg_wait_time'],
                'completed_vehicles': latest_selfish['completed_vehicles'],
                'avg_congestion': latest_selfish['avg_congestion']
            }
        
        if self.cooperative_metrics_history:
            latest_coop = list(self.cooperative_metrics_history)[-1]
            summary['cooperative_metrics'] = {
                'avg_travel_time': latest_coop['avg_travel_time'],
                'avg_wait_time': latest_coop['avg_wait_time'],
                'completed_vehicles': latest_coop['completed_vehicles'],
                'avg_congestion': latest_coop['avg_congestion']
            }
        
        return summary
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculate trend in data (positive = increasing, negative = decreasing)"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear regression slope
        x = np.arange(len(data))
        y = np.array(data)
        
        # Calculate slope
        if len(x) > 0:
            slope = np.polyfit(x, y, 1)[0]
            return slope
        
        return 0.0
    
    def calculate_fuel_consumption(self, metrics: Dict) -> float:
        """
        Calculate estimated fuel consumption
        Based on travel time and congestion
        """
        # Simplified fuel consumption model
        # More congestion and time = more fuel
        base_consumption = metrics['total_travel_time'] * 0.1  # Base consumption per time unit
        congestion_penalty = metrics['avg_congestion'] * metrics['active_vehicles'] * 0.05
        idle_consumption = metrics['total_wait_time'] * 0.05  # Idling uses fuel
        
        total_fuel = base_consumption + congestion_penalty + idle_consumption
        return total_fuel
    
    def get_comparative_analysis(self) -> Dict:
        """
        Get comparative analysis between selfish and cooperative strategies
        """
        if not self.selfish_metrics_history or not self.cooperative_metrics_history:
            return {}
        
        # Calculate averages
        selfish_avg = {
            'travel_time': np.mean([m['avg_travel_time'] for m in self.selfish_metrics_history]),
            'wait_time': np.mean([m['avg_wait_time'] for m in self.selfish_metrics_history]),
            'completed': np.mean([m['completed_vehicles'] for m in self.selfish_metrics_history]),
            'congestion': np.mean([m['avg_congestion'] for m in self.selfish_metrics_history])
        }
        
        coop_avg = {
            'travel_time': np.mean([m['avg_travel_time'] for m in self.cooperative_metrics_history]),
            'wait_time': np.mean([m['avg_wait_time'] for m in self.cooperative_metrics_history]),
            'completed': np.mean([m['completed_vehicles'] for m in self.cooperative_metrics_history]),
            'congestion': np.mean([m['avg_congestion'] for m in self.cooperative_metrics_history])
        }
        
        # Calculate improvements
        improvements = {
            'travel_time_improvement': ((selfish_avg['travel_time'] - coop_avg['travel_time']) / 
                                       selfish_avg['travel_time'] * 100) if selfish_avg['travel_time'] > 0 else 0,
            'wait_time_improvement': ((selfish_avg['wait_time'] - coop_avg['wait_time']) / 
                                     selfish_avg['wait_time'] * 100) if selfish_avg['wait_time'] > 0 else 0,
            'throughput_improvement': ((coop_avg['completed'] - selfish_avg['completed']) / 
                                      selfish_avg['completed'] * 100) if selfish_avg['completed'] > 0 else 0,
            'congestion_improvement': ((selfish_avg['congestion'] - coop_avg['congestion']) / 
                                      selfish_avg['congestion'] * 100) if selfish_avg['congestion'] > 0 else 0
        }
        
        analysis = {
            'selfish_average': selfish_avg,
            'cooperative_average': coop_avg,
            'improvements': improvements,
            'price_of_anarchy': self.current_poa,
            'winner': 'cooperative' if self.current_poa > 1.05 else 'tie'
        }
        
        return analysis
    
    def get_braess_report(self) -> Dict:
        """Get report on Braess's Paradox events"""
        if not self.braess_events:
            return {
                'events_detected': 0,
                'paradox_active': False,
                'message': 'No Braess\'s Paradox events detected'
            }
        
        latest_event = self.braess_events[-1]
        
        return {
            'events_detected': len(self.braess_events),
            'paradox_active': self.braess_detected,
            'latest_event': latest_event,
            'message': f"Braess's Paradox detected! Adding road {latest_event['road_added']} "
                      f"decreased efficiency by {(1 - latest_event['efficiency_ratio']) * 100:.1f}%"
        }
    
    def reset(self):
        """Reset analytics"""
        self.selfish_metrics_history.clear()
        self.cooperative_metrics_history.clear()
        self.poa_history = []
        self.braess_events = []
        self.current_poa = 1.0
        self.braess_detected = False
