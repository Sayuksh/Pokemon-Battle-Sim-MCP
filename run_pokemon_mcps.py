#!/usr/bin/env python3
"""
Pokémon MCP Runner Script

This script starts the Pokémon MCP servers for use with Claude or other LLM clients.
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import atexit

# Define paths to MCP server scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_MCP_PATH = os.path.join(SCRIPT_DIR, "pokemon_mcp/data_system/pokemon_mcp_server.py")
BATTLE_MCP_PATH = os.path.join(SCRIPT_DIR, "pokemon_mcp/battle_system/pokemon_battle_mcp_server.py")
INTEGRATED_MCP_PATH = os.path.join(SCRIPT_DIR, "pokemon_mcp/integration/pokemon_mcp_integration.py")

# Track running processes
processes = []

def cleanup():
    """Clean up all running processes on exit."""
    print("\nShutting down MCP servers...")
    for process in processes:
        if process.poll() is None:  # If process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    print("All servers stopped.")

# Register cleanup function to run on exit
atexit.register(cleanup)

def handle_sigint(sig, frame):
    """Handle SIGINT (Ctrl+C) gracefully."""
    print("\nReceived interrupt signal. Shutting down...")
    sys.exit(0)

# Register SIGINT handler
signal.signal(signal.SIGINT, handle_sigint)

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import mcp
        print("MCP library found.")
    except ImportError:
        print("Error: MCP library not found. Please install it with:")
        print("pip install mcp")
        return False
    
    return True

def start_server(script_path, server_name):
    """Start an MCP server as a subprocess."""
    print(f"Starting {server_name}...")
    
    # Create a new process for the server
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Add the process to our list of processes
    processes.append(process)
    
    # Wait a moment to ensure the server starts
    time.sleep(1)
    
    # Check if the process is still running
    if process.poll() is not None:
        print(f"Error: {server_name} failed to start.")
        stderr_output = process.stderr.read()
        print(f"Error output: {stderr_output}")
        return False
    
    print(f"{server_name} started successfully.")
    return True

def main():
    """Main function to parse arguments and start servers."""
    parser = argparse.ArgumentParser(description="Start Pokémon MCP servers for Claude integration.")
    parser.add_argument("--data-only", action="store_true", help="Start only the Pokémon data MCP server")
    parser.add_argument("--battle-only", action="store_true", help="Start only the Pokémon battle MCP server")
    parser.add_argument("--integrated", action="store_true", help="Start the integrated MCP server (default)")
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Determine which servers to start
    if not (args.data_only or args.battle_only or args.integrated):
        # If no specific server is requested, default to integrated
        args.integrated = True
    
    # Start requested servers
    if args.data_only:
        if not start_server(DATA_MCP_PATH, "Pokémon Data MCP Server"):
            sys.exit(1)
    
    if args.battle_only:
        if not start_server(BATTLE_MCP_PATH, "Pokémon Battle MCP Server"):
            sys.exit(1)
    
    if args.integrated:
        if not start_server(INTEGRATED_MCP_PATH, "Integrated Pokémon MCP Server"):
            sys.exit(1)
    
    # Print instructions for connecting to Claude
    print("\n" + "="*80)
    print("Pokémon MCP Servers are now running!")
    print("="*80)
    print("\nTo connect Claude to these servers:")
    print("1. Open Claude Desktop App")
    print("2. Go to Settings > MCP Servers")
    print("3. Click 'Add Server'")
    print("4. Enter the path to the server script:")
    
    if args.data_only:
        print(f"   {DATA_MCP_PATH}")
    if args.battle_only:
        print(f"   {BATTLE_MCP_PATH}")
    if args.integrated:
        print(f"   {INTEGRATED_MCP_PATH}")
    
    print("\n5. Click 'Add' and restart Claude")
    print("\nOnce connected, you can ask Claude about Pokémon or simulate battles!")
    print("\nExample queries:")
    print("- Tell me about Pikachu")
    print("- What are all the Fire-type Pokémon?")
    print("- Simulate a battle between Charizard and Blastoise")
    print("- Who would win in a fight between Mewtwo and Rayquaza?")
    
    print("\nPress Ctrl+C to stop the servers.")
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
