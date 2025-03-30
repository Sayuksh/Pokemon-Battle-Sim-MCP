from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path to import PokemonDataSystem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_system.pokemon_query_system import PokemonDataSystem
from pokemon_battle_system import PokemonBattleSystem

app = Flask(__name__)
data_system = PokemonDataSystem()
battle_system = PokemonBattleSystem(data_system)

@app.route('/api/battle/simulate', methods=['POST'])
def simulate_battle():
    """API endpoint for simulating a battle between two Pokémon."""
    data = request.get_json()
    pokemon1_name = data.get('pokemon1', '')
    pokemon2_name = data.get('pokemon2', '')
    num_turns = data.get('num_turns', 3)
    
    result = battle_system.simulate_battle(pokemon1_name, pokemon2_name, num_turns)
    return jsonify(result)

@app.route('/api/battle/initialize/<name>', methods=['GET'])
def initialize_pokemon(name):
    """API endpoint for initializing a Pokémon for battle."""
    result = battle_system.initialize_pokemon_for_battle(name)
    return jsonify(result)

@app.route('/api/battle/turn', methods=['POST'])
def simulate_turn():
    """API endpoint for simulating a single turn of battle."""
    data = request.get_json()
    attacker_data = data.get('attacker', {})
    defender_data = data.get('defender', {})
    move_name = data.get('move', 'Tackle')
    
    result = battle_system.simulate_battle_turn(attacker_data, defender_data, move_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
