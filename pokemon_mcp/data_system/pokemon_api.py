from flask import Flask, request, jsonify
from pokemon_query_system import PokemonDataSystem
import json

app = Flask(__name__)
data_system = PokemonDataSystem()

@app.route('/api/pokemon/query', methods=['POST'])
def query_pokemon():
    """API endpoint for querying Pokémon data."""
    data = request.get_json()
    query = data.get('query', '')
    
    result = data_system.query_pokemon(query)
    return jsonify(result)

@app.route('/api/pokemon/info/<name>', methods=['GET'])
def get_pokemon_info(name):
    """API endpoint for getting information about a specific Pokémon."""
    result = data_system.get_pokemon_info(name)
    return jsonify(result)

@app.route('/api/pokemon/type/<type_name>', methods=['GET'])
def get_pokemon_by_type(type_name):
    """API endpoint for getting Pokémon by type."""
    result = data_system.get_pokemon_by_type(type_name)
    return jsonify(result)

@app.route('/api/pokemon/generation/<int:gen_num>', methods=['GET'])
def get_pokemon_by_generation(gen_num):
    """API endpoint for getting Pokémon by generation."""
    result = data_system.get_pokemon_by_generation(gen_num)
    return jsonify(result)

@app.route('/api/pokemon/moves/<name>', methods=['GET'])
def get_pokemon_moves(name):
    """API endpoint for getting moves for a specific Pokémon."""
    result = data_system.get_pokemon_moves(name)
    return jsonify(result)

@app.route('/api/pokemon/all', methods=['GET'])
def get_all_pokemon_names():
    """API endpoint for getting all Pokémon names."""
    result = data_system.get_all_pokemon_names()
    return jsonify({"pokemon": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
