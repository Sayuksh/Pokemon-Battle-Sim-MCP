import asyncio
import json
import sys
import os
from mcp.server.fastmcp import FastMCP, Context
from mcp import Tool

# Add parent directory to path to import PokemonDataSystem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_system.pokemon_query_system import PokemonDataSystem
from pokemon_battle_system import PokemonBattleSystem

# Create FastMCP server
mcp = FastMCP("Pokemon Battle MCP")

# Initialize systems
data_system = PokemonDataSystem()
battle_system = PokemonBattleSystem(data_system)

@mcp.tool()
async def simulate_battle(pokemon1: str, pokemon2: str, num_turns: int = 3) -> str:
    """Simulate a battle between two Pokémon"""
    try:
        result = battle_system.simulate_battle(pokemon1, pokemon2, num_turns)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def initialize_pokemon(name: str) -> str:
    """Initialize a Pokémon for battle with default HP and moves"""
    try:
        result = battle_system.initialize_pokemon_for_battle(name)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def simulate_battle_turn(attacker: dict, defender: dict, move: str) -> str:
    """Simulate a single turn of battle between two Pokémon"""
    try:
        result = battle_system.simulate_battle_turn(attacker, defender, move)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(mcp.run())
