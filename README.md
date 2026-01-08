# 🚗 The Traffic Tamer

**Multi-Agent Traffic Simulation Platform with Game Theory and Reinforcement Learning**

A comparative laboratory demonstrating the difference between 'Selfish' (Nash Equilibrium) and 'Cooperative' (Social Optimum) driving behaviors using advanced simulation techniques.

## 🎯 Overview

The Traffic Tamer is a sophisticated traffic simulation platform that combines:
- **Game Theory**: Strategic decision-making analysis
- **Multi-Agent Reinforcement Learning (MARL)**: Cooperative learning algorithms
- **Real-time Visualization**: Interactive dashboards and live metrics
- **Analytical Tools**: Price of Anarchy and Braess's Paradox detection

## 🏗️ System Architecture

### 1. Simulation Environment (The Grid)
- Dynamic traffic grid with intersections and traffic lights
- Configurable traffic density (Rush Hour, Midnight, etc.)
- Varying road capacities with congestion modeling
- BPR (Bureau of Public Roads) travel time functions

### 2. Agent Strategy Modules (The Game Theory)

#### Selfish Agent (Nash Equilibrium)
- Uses greedy algorithms (Dijkstra/A*)
- Optimizes personal travel time only
- Recalculates routes based on current congestion
- Represents typical human driving behavior

#### Cooperative Agent (Social Optimum)
- Multi-Agent Reinforcement Learning (Q-Learning)
- Shares global reward function
- Maximizes total system throughput
- Learns from system-wide performance

### 3. Analytical Engine
- **Price of Anarchy (PoA)**: Measures efficiency loss from selfish behavior
- **Braess's Paradox Detection**: Identifies when adding roads worsens congestion
- **Comparative Metrics**: Travel time, wait time, throughput, fuel consumption

### 4. Real-Time Visualization
- **Pygame**: Native desktop visualization with real-time rendering
- **Streamlit**: Web-based interactive dashboard with charts
- Live metrics: Average Wait Time, Fuel Consumption, Total Cars Cleared

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/The-Traffic-Tamer.git
cd The-Traffic-Tamer

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulation

#### 1. Comparison Mode (Default)
Run comparative analysis between Selfish and Cooperative strategies:

```bash
python main.py --mode comparison --episodes 10
```

#### 2. Pygame Visualization
Interactive desktop visualization:

```bash
python main.py --mode pygame --agent-type mixed
```

#### 3. Streamlit Dashboard
Web-based interactive dashboard:

```bash
streamlit run app_streamlit.py
```

Then open your browser to `http://localhost:8501`

## 🎮 Usage Examples

### Run Specific Agent Types

```bash
# Run only selfish agents
python main.py --mode pygame --agent-type selfish

# Run only cooperative agents
python main.py --mode pygame --agent-type cooperative

# Run mixed agents (default)
python main.py --mode pygame --agent-type mixed
```

### Custom Configuration

Edit `config.yaml` to customize:
- Traffic density
- Number of vehicles
- Grid size
- Learning parameters
- Visualization settings

Example configuration:

```yaml
simulation:
  grid_width: 10
  grid_height: 10
  num_vehicles: 50
  traffic_density: 'rush_hour'  # Options: low, medium, high, rush_hour, midnight
```

## 📊 Key Metrics

### Price of Anarchy (PoA)
```
PoA = (Nash Equilibrium Cost) / (Social Optimum Cost)
```
- **PoA = 1.0**: Both strategies equally efficient
- **PoA > 1.0**: Selfish behavior reduces efficiency
- **Higher PoA**: Greater cost of selfishness

### Braess's Paradox
Detects situations where:
- Adding road capacity **increases** congestion
- System efficiency decreases after infrastructure improvements
- Counterintuitive traffic patterns emerge

## 🧪 Features

### Core Capabilities
- ✅ Dynamic traffic grid with intersections
- ✅ Traffic lights with configurable cycles
- ✅ Road capacity and congestion modeling
- ✅ Selfish agents using Dijkstra/A* pathfinding
- ✅ Cooperative agents using Q-Learning MARL
- ✅ Price of Anarchy calculation
- ✅ Braess's Paradox detection
- ✅ Real-time Pygame visualization
- ✅ Interactive Streamlit dashboard
- ✅ Comparative analysis tools
- ✅ Time series charts and metrics

### Analytics
- Average wait time tracking
- Average travel time measurement
- Throughput analysis (vehicles completed)
- Congestion level monitoring
- Fuel consumption estimation
- System efficiency calculations

## 🛠️ Tech Stack

- **Python 3.8+**: Core language
- **NetworkX**: Graph algorithms and pathfinding
- **NumPy**: Numerical computations
- **Pygame**: Desktop visualization
- **Streamlit**: Web dashboard
- **Plotly**: Interactive charts
- **Ray RLlib**: Reinforcement learning (extensible)
- **PettingZoo**: Multi-agent environment framework (compatible)
- **PyYAML**: Configuration management

## 📁 Project Structure

```
The-Traffic-Tamer/
├── traffic_tamer/
│   ├── __init__.py           # Package initialization
│   ├── environment.py        # Traffic environment, roads, lights
│   ├── agents.py             # Selfish and Cooperative agents
│   ├── analytics.py          # PoA and Braess's Paradox detection
│   ├── simulation.py         # Simulation controller
│   ├── visualization.py      # Pygame visualizer
│   └── dashboard.py          # Streamlit dashboard
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point
├── app_streamlit.py          # Streamlit app
└── README.md                 # This file
```

## 🎓 Educational Value

This platform demonstrates:
1. **Nash Equilibrium**: Stable state where no agent benefits from changing strategy
2. **Social Optimum**: Globally optimal state maximizing collective welfare
3. **Price of Anarchy**: Quantifies efficiency loss from lack of coordination
4. **Braess's Paradox**: Shows counterintuitive network behavior
5. **Multi-Agent Learning**: Agents learning in shared environments
6. **Game Theory Applications**: Real-world strategic decision-making

## 📈 Expected Results

Typical findings:
- Cooperative agents achieve **15-30% better** average travel times
- Price of Anarchy ranges from **1.2 to 1.8** in congested scenarios
- Braess's Paradox can be detected by adding strategic roads
- System throughput improves **20-40%** with cooperative behavior

## 🔬 Research Applications

This platform can be used to study:
- Traffic optimization algorithms
- Multi-agent coordination strategies
- Reinforcement learning in traffic systems
- Game-theoretic equilibria in transportation
- Infrastructure planning and road network design
- Congestion pricing and management policies

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional pathfinding algorithms (D*, RRT)
- Advanced MARL algorithms (PPO, A3C, QMIX)
- More complex road networks
- Vehicle-to-vehicle communication
- Dynamic traffic lights optimization
- 3D visualization

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Game Theory concepts from classical transportation economics
- MARL techniques from recent reinforcement learning research
- Traffic flow models based on transportation engineering principles

## 📧 Contact

For questions, suggestions, or collaborations:
- GitHub: [@yadavanujkumar](https://github.com/yadavanujkumar)
- Repository: [The-Traffic-Tamer](https://github.com/yadavanujkumar/The-Traffic-Tamer)

---

**Built with ❤️ for exploring the intersection of Game Theory, Reinforcement Learning, and Traffic Management**