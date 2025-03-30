import asyncio
import json
import sys
import os
from mcp.server.fastmcp import FastMCP, Context
from mcp import Tool

# Add parent directory to path to import PokemonDataSystem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pokemon_query_system import PokemonDataSystem

# Create FastMCP server
mcp = FastMCP("Pokemon Data MCP")

# Initialize data system
data_system = PokemonDataSystem()

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
    """Get a list of Pokémon that have the specified type"""
    try:
        result = data_system.get_pokemon_by_type(type_name)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_pokemon_by_generation(generation: int) -> str:
    """Get a list of Pokémon from a specific generation"""
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

@mcp.tool()
async def get_all_pokemon_names() -> str:
    """Get a list of all Pokémon names"""
    try:
        result = data_system.get_all_pokemon_names()
        return json.dumps({"pokemon": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(mcp.run())
