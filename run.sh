#!/bin/bash
# Quick run script for different modes

echo "Traffic Tamer - Quick Run Script"
echo "================================"
echo ""
echo "Choose a mode:"
echo "1. Run quick example"
echo "2. Run comparison mode (10 episodes)"
echo "3. Start Streamlit dashboard"
echo "4. Run tests"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Running quick example..."
        python example.py
        ;;
    2)
        echo "Running comparison mode..."
        python main.py --mode comparison --episodes 10
        ;;
    3)
        echo "Starting Streamlit dashboard..."
        echo "Open http://localhost:8501 in your browser"
        streamlit run app_streamlit.py
        ;;
    4)
        echo "Running tests..."
        python tests/test_traffic_tamer.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
