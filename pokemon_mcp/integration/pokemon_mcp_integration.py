import asyncio
import json
import sys
import os
import re
from mcp.server.fastmcp import FastMCP, Context
from mcp import Tool

# Add parent directory to path to import PokemonDataSystem and PokemonBattleSystem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_system.pokemon_query_system import PokemonDataSystem
from battle_system.pokemon_battle_system import PokemonBattleSystem

# Create FastMCP server
mcp = FastMCP("Pokémon MCP Integration")

# Initialize systems
data_system = PokemonDataSystem()
battle_system = PokemonBattleSystem(data_system)

# Data System Tools
@mcp.tool()
async def get_pokemon_info(name: str) -> str:
    """Get detailed information about a specific Pokémon by name"""
    try:
        result = data_system.get_pokemon_info(name)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_pokemon_by_type(type_name: str) -> str:
    """Get all Pokémon of a specific type"""
    try:
        result = data_system.get_pokemon_by_type(type_name)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_pokemon_by_generation(generation: int) -> str:
    """Get all Pokémon from a specific generation"""
    try:
        result = data_system.get_pokemon_by_generation(generation)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def query_pokemon(query: str) -> str:
    """Query Pokémon data using natural language"""
    try:
        result = data_system.query_pokemon(query)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Battle System Tools
@mcp.tool()
async def simulate_battle(pokemon1: str, pokemon2: str, num_turns: int = 3) -> str:
    """Simulate a battle between two Pokémon"""
    try:
        result = battle_system.simulate_battle(pokemon1, pokemon2, num_turns)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Unified Tool for Natural Language Processing
@mcp.tool()
async def pokemon_assistant(query: str) -> str:
    """
    Handle pokemon_assistant tool calls by intelligently routing to the appropriate subsystem.
    This is the main entry point for natural language processing.
    """
    try:
        query = query.lower()
        
        # Check if it's a battle simulation request
        battle_patterns = [
            r"battle between (.+?) and (.+)",
            r"(.+?) vs\.? (.+)",
            r"(.+?) fight (.+)",
            r"(.+?) against (.+)",
            r"simulate (?:a )?battle (?:between )?(.+?) and (.+)"
        ]
        
        for pattern in battle_patterns:
            match = re.search(pattern, query)
            if match:
                pokemon1 = match.group(1).strip().capitalize()
                pokemon2 = match.group(2).strip().capitalize()
                
                # Extract number of turns if specified
                turns_match = re.search(r"(\d+) turns", query)
                num_turns = int(turns_match.group(1)) if turns_match else 3
                
                result = battle_system.simulate_battle(pokemon1, pokemon2, num_turns)
                
                # Format the battle result in a more readable way
                if "error" not in result:
                    battle_summary = {
                        "battle_summary": f"Battle between {pokemon1} and {pokemon2} for {num_turns} turns",
                        "winner": result["winner"],
                        "final_hp": {
                            f"{result['pokemon1']['name']}": f"{result['pokemon1']['ending_hp']}/{result['pokemon1']['starting_hp']} HP",
                            f"{result['pokemon2']['name']}": f"{result['pokemon2']['ending_hp']}/{result['pokemon2']['starting_hp']} HP"
                        },
                        "battle_log": [log["battle_log"] for log in result["battle_log"]]
                    }
                    return json.dumps(battle_summary)
                
                return json.dumps(result)
        
        # If not a battle request, treat as a data query
        result = data_system.query_pokemon(query)
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "help": "You can ask about Pokémon data (e.g., 'Tell me about Pikachu') or request a battle simulation (e.g., 'Simulate a battle between Charizard and Blastoise')"
        })

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(mcp.run())
