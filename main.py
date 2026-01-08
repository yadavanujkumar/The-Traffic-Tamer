#!/usr/bin/env python3
"""
Main entry point for Traffic Tamer simulation
Supports both Pygame and Streamlit modes
"""

import argparse
import sys
from traffic_tamer.simulation import SimulationController


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Traffic Tamer - Multi-Agent Traffic Simulation Platform"
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['pygame', 'streamlit', 'comparison'],
        default='comparison',
        help='Visualization mode (default: comparison)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--episodes',
        type=int,
        default=10,
        help='Number of episodes for comparison mode (default: 10)'
    )
    
    parser.add_argument(
        '--agent-type',
        type=str,
        choices=['selfish', 'cooperative', 'mixed'],
        default='mixed',
        help='Agent type for single runs (default: mixed)'
    )
    
    args = parser.parse_args()
    
    # Create simulation controller
    controller = SimulationController(args.config)
    
    try:
        if args.mode == 'pygame':
            print("Starting Pygame visualization...")
            controller.run_interactive()
        elif args.mode == 'streamlit':
            print("Starting Streamlit dashboard...")
            print("Please run: streamlit run app_streamlit.py")
        elif args.mode == 'comparison':
            print("Running comparative analysis...")
            controller.run_comparison(args.episodes)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    finally:
        controller.close()


if __name__ == '__main__':
    main()
