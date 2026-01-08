# Developer Documentation

## Architecture Overview

The Traffic Tamer is organized into several key modules:

### 1. Environment Module (`traffic_tamer/environment.py`)

**Core Classes:**
- `TrafficLight`: Manages traffic light states (GREEN, YELLOW, RED)
- `Road`: Represents road segments with capacity and congestion
- `TrafficEnvironment`: Main simulation environment

**Key Features:**
- Grid-based road network using NetworkX
- Dynamic traffic light cycles
- BPR (Bureau of Public Roads) travel time function
- Congestion-based routing weights

### 2. Agents Module (`traffic_tamer/agents.py`)

**Core Classes:**
- `Agent`: Abstract base class for all agents
- `SelfishAgent`: Nash Equilibrium strategy using Dijkstra/A*
- `CooperativeAgent`: Social Optimum strategy using Q-Learning
- `AgentManager`: Factory for creating and managing agents

**Agent Strategies:**

#### Selfish Agent (Nash Equilibrium)
```python
# Uses greedy pathfinding
path = nx.dijkstra_path(env.graph, start, goal, weight='weight')
# Recalculates based on current congestion
```

#### Cooperative Agent (Social Optimum)
```python
# Uses Q-Learning with global reward
reward = calculate_global_reward(env, vehicle_id)
update_q_value(state, action, reward, next_state)
```

### 3. Analytics Module (`traffic_tamer/analytics.py`)

**Core Class:**
- `Analytics`: Calculates metrics and detects patterns

**Key Metrics:**
- **Price of Anarchy (PoA)**: `Nash Cost / Social Optimum Cost`
- **Braess's Paradox**: Detects efficiency decrease after adding roads
- **System Efficiency**: `Throughput / (Travel Time + Wait Time)`

### 4. Visualization Modules

#### Pygame (`traffic_tamer/visualization.py`)
- Real-time desktop rendering
- Color-coded congestion display
- Live metrics panel

#### Streamlit (`traffic_tamer/dashboard.py`)
- Web-based interactive dashboard
- Plotly charts for time series
- Network graph visualization

### 5. Simulation Controller (`traffic_tamer/simulation.py`)

**Core Class:**
- `SimulationController`: Orchestrates simulation runs

**Modes:**
- Interactive: Real-time visualization with Pygame
- Comparison: Run multiple episodes and compare strategies
- Streamlit: Web-based dashboard

## Configuration

Edit `config.yaml` to customize:

```yaml
simulation:
  num_intersections: 16    # Grid size (must be perfect square)
  road_capacity: 10        # Vehicles per road
  traffic_density: medium  # low, medium, high, rush_hour, midnight
  
agents:
  selfish:
    algorithm: dijkstra    # dijkstra, astar
  cooperative:
    algorithm: qlearning   # qlearning, (ppo extensible)
    learning_rate: 0.001
```

## Extending the System

### Adding New Agent Types

1. Create a new agent class inheriting from `Agent`:

```python
class MyCustomAgent(Agent):
    def plan_route(self, env, start, goal):
        # Custom routing logic
        pass
    
    def get_action(self, env, vehicle_id):
        # Custom action selection
        pass
```

2. Register in `AgentManager.create_agent()`:

```python
elif agent_type == 'custom':
    agent = MyCustomAgent(agent_id)
```

### Adding New Metrics

1. Add calculation in `Analytics`:

```python
def calculate_new_metric(self, metrics: Dict) -> float:
    # Your calculation
    return value
```

2. Include in `get_system_performance_summary()`:

```python
summary['new_metric'] = self.calculate_new_metric(metrics)
```

### Adding New Visualizations

For Streamlit, add to `dashboard.py`:

```python
def render_new_chart(self, data):
    fig = px.line(data, x='step', y='metric')
    st.plotly_chart(fig)
```

## Algorithm Details

### Travel Time Function (BPR)

```python
travel_time = (length / base_speed) * (1 + 0.15 * (congestion ** 4))
```

Where:
- `length`: Road segment length
- `base_speed`: Free-flow speed
- `congestion`: Ratio of vehicles to capacity (0.0 to 1.0)

### Q-Learning Update

```python
Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
```

Where:
- `α`: Learning rate
- `γ`: Discount factor
- `r`: Reward
- `s, s'`: Current and next state
- `a, a'`: Current and next action

### Price of Anarchy

```python
PoA = Σ(cost_i_nash) / Σ(cost_i_social)
```

Where cost includes travel time and wait time.

## Testing

Run tests with:

```bash
python tests/test_traffic_tamer.py
```

Test coverage:
- Environment initialization
- Traffic light cycles
- Road congestion
- Agent pathfinding
- Analytics calculations
- Integration tests

## Performance Considerations

**Optimization Tips:**

1. **Grid Size**: Larger grids (> 25 nodes) increase computation
2. **Vehicle Count**: More vehicles = more pathfinding
3. **Recalculation Frequency**: Lower frequency = faster but less adaptive
4. **Learning Rate**: Higher = faster convergence but less stable

**Typical Performance:**
- 16 node grid, 50 vehicles: ~30 FPS (Pygame)
- 100 episodes comparison: ~2-5 minutes

## Common Issues

### Issue: Agents not reaching goals
**Solution**: Check graph connectivity, increase max_steps

### Issue: PoA always 1.0
**Solution**: Need more episodes for statistics, check if metrics are being recorded

### Issue: Pygame window not opening
**Solution**: Check SDL dependencies, try Streamlit mode instead

## API Reference

### Environment

```python
env = TrafficEnvironment(config)
env.spawn_vehicle(start, goal, agent_type)
env.move_vehicle(vehicle_id, next_position)
env.step()  # Returns metrics
env.reset()
```

### Agents

```python
agent = AgentManager(config).create_agent('selfish')
path = agent.plan_route(env, start, goal)
action = agent.get_action(env, vehicle_id)
```

### Analytics

```python
analytics = Analytics(config)
analytics.record_metrics(metrics, 'selfish')
poa = analytics.calculate_price_of_anarchy()
summary = analytics.get_system_performance_summary()
```

## Contributing Guidelines

1. Follow PEP 8 style guide
2. Add docstrings to all functions
3. Write unit tests for new features
4. Update documentation
5. Test with both agent types

## Future Enhancements

Planned features:
- [ ] PPO algorithm for cooperative agents
- [ ] Vehicle-to-vehicle communication
- [ ] Dynamic traffic light optimization
- [ ] 3D visualization
- [ ] Real map data integration
- [ ] Multi-objective optimization
- [ ] Advanced MARL algorithms (QMIX, COMA)
