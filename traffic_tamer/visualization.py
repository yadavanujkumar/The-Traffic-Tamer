"""
Visualization Module
Real-time visualization using Pygame
"""

import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional


class PygameVisualizer:
    """Pygame-based real-time visualization"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.width = config['visualization']['window_width']
        self.height = config['visualization']['window_height']
        self.fps = config['visualization']['fps']
        
        # Colors
        colors = config['visualization']['colors']
        self.color_road = tuple(colors['road'])
        self.color_intersection = tuple(colors['intersection'])
        self.color_selfish = tuple(colors['selfish_agent'])
        self.color_cooperative = tuple(colors['cooperative_agent'])
        self.color_red = tuple(colors['traffic_light_red'])
        self.color_green = tuple(colors['traffic_light_green'])
        self.color_yellow = tuple(colors['traffic_light_yellow'])
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Traffic Tamer - Multi-Agent Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Layout
        self.grid_area = (50, 50, self.width - 300, self.height - 100)
        self.metrics_area = (self.width - 280, 50, 260, self.height - 100)
        
    def render(self, env, analytics: Optional[object] = None):
        """Render the current state"""
        self.screen.fill((255, 255, 255))
        
        # Draw grid
        self._draw_grid(env)
        
        # Draw roads
        self._draw_roads(env)
        
        # Draw traffic lights
        self._draw_traffic_lights(env)
        
        # Draw vehicles
        self._draw_vehicles(env)
        
        # Draw metrics
        if analytics:
            self._draw_metrics(env, analytics)
        
        pygame.display.flip()
        self.clock.tick(self.fps)
        
    def _draw_grid(self, env):
        """Draw the grid background"""
        x, y, w, h = self.grid_area
        pygame.draw.rect(self.screen, (240, 240, 240), (x, y, w, h))
        
        # Draw grid lines
        nodes_per_row = int(np.sqrt(env.num_intersections))
        cell_width = w // nodes_per_row
        cell_height = h // nodes_per_row
        
        for i in range(nodes_per_row + 1):
            # Vertical lines
            pygame.draw.line(self.screen, (200, 200, 200),
                           (x + i * cell_width, y),
                           (x + i * cell_width, y + h), 1)
            # Horizontal lines
            pygame.draw.line(self.screen, (200, 200, 200),
                           (x, y + i * cell_height),
                           (x + w, y + i * cell_height), 1)
    
    def _get_screen_position(self, env, node_id: int) -> Tuple[int, int]:
        """Get screen position for a node"""
        pos = env.graph.nodes[node_id]['pos']
        nodes_per_row = int(np.sqrt(env.num_intersections))
        
        x, y, w, h = self.grid_area
        cell_width = w // nodes_per_row
        cell_height = h // nodes_per_row
        
        screen_x = x + pos[0] * cell_width + cell_width // 2
        screen_y = y + pos[1] * cell_height + cell_height // 2
        
        return (screen_x, screen_y)
    
    def _draw_roads(self, env):
        """Draw roads with congestion visualization"""
        for (start, end), road in env.roads.items():
            start_pos = self._get_screen_position(env, start)
            end_pos = self._get_screen_position(env, end)
            
            # Color based on congestion
            congestion = road.get_congestion()
            color = self._get_congestion_color(congestion)
            
            # Draw road
            width = max(3, int(5 * (1 + congestion)))
            pygame.draw.line(self.screen, color, start_pos, end_pos, width)
            
            # Draw vehicle count
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            count_text = self.small_font.render(str(len(road.vehicles)), True, (0, 0, 0))
            self.screen.blit(count_text, (mid_x - 5, mid_y - 5))
    
    def _get_congestion_color(self, congestion: float) -> Tuple[int, int, int]:
        """Get color based on congestion level"""
        # Green (low) to Yellow to Red (high)
        if congestion < 0.3:
            return (0, 255, 0)
        elif congestion < 0.6:
            return (255, 255, 0)
        else:
            return (255, 0, 0)
    
    def _draw_traffic_lights(self, env):
        """Draw traffic lights at intersections"""
        for node_id, light in env.traffic_lights.items():
            pos = self._get_screen_position(env, node_id)
            
            # Choose color based on state
            if light.state.name == 'GREEN':
                color = self.color_green
            elif light.state.name == 'YELLOW':
                color = self.color_yellow
            else:
                color = self.color_red
            
            # Draw traffic light
            pygame.draw.circle(self.screen, color, pos, 8)
            pygame.draw.circle(self.screen, (0, 0, 0), pos, 8, 2)
    
    def _draw_vehicles(self, env):
        """Draw vehicles"""
        for vehicle in env.vehicles.values():
            if vehicle['completed']:
                continue
            
            pos = self._get_screen_position(env, vehicle['current_position'])
            
            # Choose color based on agent type
            color = self.color_selfish if vehicle['agent_type'] == 'selfish' else self.color_cooperative
            
            # Draw vehicle
            pygame.draw.circle(self.screen, color, pos, 6)
            pygame.draw.circle(self.screen, (0, 0, 0), pos, 6, 1)
    
    def _draw_metrics(self, env, analytics):
        """Draw metrics panel"""
        x, y, w, h = self.metrics_area
        
        # Background
        pygame.draw.rect(self.screen, (250, 250, 250), (x, y, w, h))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, w, h), 2)
        
        # Title
        title = self.font.render("Metrics", True, (0, 0, 0))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Get metrics
        metrics = env._collect_metrics()
        summary = analytics.get_system_performance_summary()
        
        # Draw metrics
        y_offset = y + 50
        line_height = 25
        
        metrics_to_show = [
            f"Step: {metrics['step']}",
            f"Active: {metrics['active_vehicles']}",
            f"Completed: {metrics['completed_vehicles']}",
            f"Avg Wait: {metrics['avg_wait_time']:.2f}",
            f"Avg Travel: {metrics['avg_travel_time']:.2f}",
            f"Congestion: {metrics['avg_congestion']:.2%}",
            "",
            f"Price of Anarchy:",
            f"  {summary['current_poa']:.3f}",
            "",
            f"Braess Events:",
            f"  {summary['braess_events_count']}"
        ]
        
        for line in metrics_to_show:
            text = self.small_font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (x + 10, y_offset))
            y_offset += line_height
    
    def handle_events(self) -> bool:
        """Handle Pygame events, return False to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def close(self):
        """Close the visualizer"""
        pygame.quit()
