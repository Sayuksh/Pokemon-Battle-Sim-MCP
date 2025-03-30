import sys
import os
import random
import json
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path to import PokemonDataSystem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_system.pokemon_query_system import PokemonDataSystem

class PokemonBattleSystem:
    def __init__(self, data_system: Optional[PokemonDataSystem] = None):
        """
        Initialize the Pokémon battle system.
        
        Args:
            data_system: PokemonDataSystem instance for accessing Pokémon data
        """
        self.data_system = data_system or PokemonDataSystem()
        self.type_effectiveness = self._load_type_effectiveness()
        
    def _load_type_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """Load type effectiveness chart."""
        # Simplified type effectiveness chart
        effectiveness = {
            "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
            "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
            "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
            "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
            "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
            "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
            "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
            "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
            "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
            "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
            "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
            "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
            "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
            "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
            "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
            "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
            "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
            "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5}
        }
        return effectiveness
    
    def calculate_type_effectiveness(self, move_type: str, defender_types: List[str]) -> float:
        """Calculate type effectiveness multiplier."""
        multiplier = 1.0
        move_type = move_type.capitalize()
        
        for def_type in defender_types:
            def_type = def_type.capitalize()
            if move_type in self.type_effectiveness and def_type in self.type_effectiveness[move_type]:
                multiplier *= self.type_effectiveness[move_type][def_type]
        
        return multiplier
    
    def calculate_damage(self, attacker: Dict[str, Any], defender: Dict[str, Any], 
                         move: Dict[str, Any]) -> Tuple[int, str]:
        """Calculate damage for a move."""
        # Extract relevant data
        move_power = move.get("power", 50)  # Default power if not specified
        move_type = move.get("type", "Normal")
        move_category = move.get("category", "Physical")
        
        attacker_types = attacker.get("types", ["Normal"])
        defender_types = defender.get("types", ["Normal"])
        
        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move_type in attacker_types else 1.0
        
        # Type effectiveness
        type_effectiveness = self.calculate_type_effectiveness(move_type, defender_types)
        
        # Select relevant stats based on move category
        if move_category == "Physical":
            attack_stat = attacker["stats"]["attack"]
            defense_stat = defender["stats"]["defense"]
        else:  # Special
            attack_stat = attacker["stats"]["sp_attack"]
            defense_stat = defender["stats"]["sp_defense"]
        
        # Basic damage formula (simplified from actual games)
        level = 50  # Default level
        base_damage = ((2 * level / 5 + 2) * move_power * attack_stat / defense_stat) / 50 + 2
        
        # Apply modifiers
        modifier = stab * type_effectiveness * random.uniform(0.85, 1.0)
        final_damage = max(1, int(base_damage * modifier))
        
        # Create effectiveness message
        if type_effectiveness > 1.5:
            effectiveness_msg = "It's super effective!"
        elif type_effectiveness < 0.5:
            effectiveness_msg = "It's not very effective..."
        elif type_effectiveness == 0:
            effectiveness_msg = "It has no effect..."
            final_damage = 0
        else:
            effectiveness_msg = ""
        
        return final_damage, effectiveness_msg
    
    def simulate_battle_turn(self, attacker_data: Dict[str, Any], defender_data: Dict[str, Any], 
                            move_name: str) -> Dict[str, Any]:
        """Simulate a single turn of battle."""
        # Create a simple move object (in a real implementation, this would come from a moves database)
        # For simplicity, we're creating a basic move with some default properties
        move = {
            "name": move_name,
            "type": "Normal",  # Default type
            "power": 50,       # Default power
            "category": "Physical",  # Default category
            "accuracy": 100,   # Default accuracy
            "pp": 20           # Default PP
        }
        
        # Try to get more accurate move data (this is simplified)
        if move_name.lower() == "tackle":
            move = {"name": "Tackle", "type": "Normal", "power": 40, "category": "Physical", "accuracy": 100, "pp": 35}
        elif move_name.lower() == "ember":
            move = {"name": "Ember", "type": "Fire", "power": 40, "category": "Special", "accuracy": 100, "pp": 25}
        elif move_name.lower() == "water gun":
            move = {"name": "Water Gun", "type": "Water", "power": 40, "category": "Special", "accuracy": 100, "pp": 25}
        elif move_name.lower() == "thundershock":
            move = {"name": "Thundershock", "type": "Electric", "power": 40, "category": "Special", "accuracy": 100, "pp": 30}
        
        # Calculate damage
        damage, effectiveness_msg = self.calculate_damage(attacker_data, defender_data, move)
        
        # Apply damage to defender's HP
        defender_data["current_hp"] = defender_data.get("current_hp", defender_data["stats"]["hp"])
        defender_data["current_hp"] = max(0, defender_data["current_hp"] - damage)
        
        # Check if fainted
        fainted = defender_data["current_hp"] <= 0
        
        # Create battle log
        battle_log = f"{attacker_data['name']} used {move['name']}!"
        if damage > 0:
            battle_log += f" {effectiveness_msg}" if effectiveness_msg else ""
            battle_log += f" It dealt {damage} damage!"
        else:
            battle_log += f" {effectiveness_msg}"
        
        if fainted:
            battle_log += f" {defender_data['name']} fainted!"
        
        return {
            "attacker": attacker_data["name"],
            "defender": defender_data["name"],
            "move_used": move["name"],
            "damage_dealt": damage,
            "effectiveness_message": effectiveness_msg,
            "defender_hp_remaining": defender_data["current_hp"],
            "defender_fainted": fainted,
            "battle_log": battle_log
        }
    
    def initialize_pokemon_for_battle(self, pokemon_name: str) -> Dict[str, Any]:
        """Initialize a Pokémon for battle with default HP and stats."""
        pokemon_data = self.data_system.get_pokemon_info(pokemon_name)
        
        if "error" in pokemon_data:
            return pokemon_data
        
        # Add current HP equal to max HP
        pokemon_data["current_hp"] = pokemon_data["stats"]["hp"]
        
        # Add some default moves (in a real implementation, these would come from a database)
        # For simplicity, we're adding some basic moves
        pokemon_data["moves"] = ["Tackle"]
        
        # Add type-specific moves
        if "Fire" in pokemon_data["types"]:
            pokemon_data["moves"].append("Ember")
        if "Water" in pokemon_data["types"]:
            pokemon_data["moves"].append("Water Gun")
        if "Electric" in pokemon_data["types"]:
            pokemon_data["moves"].append("Thundershock")
        
        return pokemon_data
    
    def simulate_battle(self, pokemon1_name: str, pokemon2_name: str, 
                       num_turns: int = 3) -> Dict[str, Any]:
        """Simulate a battle between two Pokémon for a specified number of turns."""
        # Initialize Pokémon
        pokemon1 = self.initialize_pokemon_for_battle(pokemon1_name)
        pokemon2 = self.initialize_pokemon_for_battle(pokemon2_name)
        
        if "error" in pokemon1:
            return {"error": f"Error with first Pokémon: {pokemon1['error']}"}
        
        if "error" in pokemon2:
            return {"error": f"Error with second Pokémon: {pokemon2['error']}"}
        
        battle_log = []
        current_turn = 1
        
        # Determine which Pokémon goes first based on Speed stat
        if pokemon1["stats"]["speed"] >= pokemon2["stats"]["speed"]:
            first_pokemon, second_pokemon = pokemon1, pokemon2
        else:
            first_pokemon, second_pokemon = pokemon2, pokemon1
        
        # Simulate battle turns
        while current_turn <= num_turns and pokemon1["current_hp"] > 0 and pokemon2["current_hp"] > 0:
            # First Pokémon's turn
            move_to_use = random.choice(first_pokemon["moves"])
            turn_result = self.simulate_battle_turn(first_pokemon, second_pokemon, move_to_use)
            battle_log.append(turn_result)
            
            # Check if second Pokémon fainted
            if second_pokemon["current_hp"] <= 0:
                break
            
            # Second Pokémon's turn
            move_to_use = random.choice(second_pokemon["moves"])
            turn_result = self.simulate_battle_turn(second_pokemon, first_pokemon, move_to_use)
            battle_log.append(turn_result)
            
            current_turn += 1
        
        # Determine battle outcome
        if pokemon1["current_hp"] <= 0:
            winner = pokemon2["name"]
        elif pokemon2["current_hp"] <= 0:
            winner = pokemon1["name"]
        else:
            # If no one fainted, the winner is the one with higher HP percentage
            hp1_percentage = pokemon1["current_hp"] / pokemon1["stats"]["hp"]
            hp2_percentage = pokemon2["current_hp"] / pokemon2["stats"]["hp"]
            winner = pokemon1["name"] if hp1_percentage >= hp2_percentage else pokemon2["name"]
        
        return {
            "pokemon1": {
                "name": pokemon1["name"],
                "starting_hp": pokemon1["stats"]["hp"],
                "ending_hp": pokemon1["current_hp"]
            },
            "pokemon2": {
                "name": pokemon2["name"],
                "starting_hp": pokemon2["stats"]["hp"],
                "ending_hp": pokemon2["current_hp"]
            },
            "num_turns_simulated": current_turn - 1,
            "battle_log": battle_log,
            "winner": winner
        }


# Example usage
if __name__ == "__main__":
    data_system = PokemonDataSystem()
    battle_system = PokemonBattleSystem(data_system)
    
    result = battle_system.simulate_battle("Charizard", "Blastoise")
    print(json.dumps(result, indent=2))
