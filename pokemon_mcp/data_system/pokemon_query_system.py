import os
import pandas as pd
import re
from typing import Dict, List, Any, Optional, Union

class PokemonDataSystem:
    def __init__(self, data_dir: str = None):
        """
        Initialize the Pokémon data system by loading data from CSV files.
        
        Args:
            data_dir: Directory containing Pokémon data CSV files
        """
        if data_dir is None:
            # Use absolute path instead of relative path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_dir = os.path.join(base_dir, "PokemonData")
        else:
            self.data_dir = data_dir
            
        self.pokemon_df = self._load_pokemon_data()
        
    def _load_pokemon_data(self) -> pd.DataFrame:
        """Load all Pokémon data from CSV files and combine into a single DataFrame."""
        all_data = []
        
        # Get all CSV files in the data directory
        csv_files = [f for f in os.listdir(self.data_dir) if f.startswith('gen') and f.endswith('.csv')]
        
        for file in sorted(csv_files):
            file_path = os.path.join(self.data_dir, file)
            gen_df = pd.read_csv(file_path)
            
            # Extract generation number from filename (e.g., 'gen01.csv' -> 1)
            gen_num = int(re.search(r'gen(\d+)', file).group(1))
            gen_df['Generation'] = gen_num
            
            all_data.append(gen_df)
        
        # Combine all DataFrames
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            raise FileNotFoundError(f"No Pokémon data CSV files found in {self.data_dir}")
    
    def query_pokemon(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about Pokémon data.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing query results
        """
        query = query.lower()
        
        # Check if query is about a specific Pokémon
        if "pokémon" in query or "pokemon" in query:
            pokemon_name_match = re.search(r'(?:about|on|for|is|does)\s+(\w+)', query)
            if pokemon_name_match:
                pokemon_name = pokemon_name_match.group(1).capitalize()
                return self.get_pokemon_info(pokemon_name)
        
        # Check for type queries
        if "type" in query:
            type_match = re.search(r'type\s+(\w+)', query)
            if type_match:
                type_name = type_match.group(1).capitalize()
                return self.get_pokemon_by_type(type_name)
        
        # Check for generation queries
        if "generation" in query:
            gen_match = re.search(r'generation\s+(\d+)', query)
            if gen_match:
                gen_num = int(gen_match.group(1))
                return self.get_pokemon_by_generation(gen_num)
        
        # Default response for unrecognized queries
        return {
            "error": "I couldn't understand your query. Try asking about a specific Pokémon, type, or generation."
        }
    
    def get_pokemon_info(self, name: str) -> Dict[str, Any]:
        """Get information about a specific Pokémon by name."""
        # Print debugging information
        print(f"Searching for Pokémon: {name}")
        print(f"Available Pokémon names: {self.pokemon_df['Name'].unique()[:10]}...")  # Show first 10 names
        
        # Capitalize the first letter of the name for better matching
        if name and len(name) > 0:
            name = name[0].upper() + name[1:].lower() if len(name) > 1 else name.upper()
        
        print(f"Normalized name for search: {name}")
        
        # Try exact match first (case-sensitive with proper capitalization)
        pokemon = self.pokemon_df[self.pokemon_df['Name'] == name]
        
        # If no match, try case-insensitive match
        if len(pokemon) == 0:
            print(f"No exact match for {name}, trying case-insensitive match")
            pokemon = self.pokemon_df[self.pokemon_df['Name'].str.lower() == name.lower()]
        
        # If still no match, try partial match
        if len(pokemon) == 0:
            print(f"No case-insensitive match for {name}, trying partial match")
            pokemon = self.pokemon_df[self.pokemon_df['Name'].str.lower().str.contains(name.lower())]
        
        if len(pokemon) == 0:
            return {"error": f"No Pokémon found with name {name}"}
        
        pokemon = pokemon.iloc[0]
        return {
            "name": pokemon['Name'],
            "id": int(pokemon['ID']),
            "types": [t for t in [pokemon.get('Type1'), pokemon.get('Type2')] if pd.notna(t) and t != " "],
            "stats": {
                "hp": int(pokemon['HP']),
                "attack": int(pokemon['Attack']),
                "defense": int(pokemon['Defense']),
                "sp_attack": int(pokemon['Sp. Atk']),
                "sp_defense": int(pokemon['Sp. Def']),
                "speed": int(pokemon['Speed'])
            },
            "generation": int(pokemon['Generation']),
            "abilities": []  # No abilities in the CSV, but keeping the field for compatibility
        }
    
    def get_pokemon_by_type(self, type_name: str) -> Dict[str, Any]:
        """Get all Pokémon of a specific type."""
        type_pokemon = self.pokemon_df[
            (self.pokemon_df['Type1'].str.lower() == type_name.lower()) | 
            (self.pokemon_df['Type2'].str.lower() == type_name.lower())
        ]
        
        if len(type_pokemon) == 0:
            return {"error": f"No Pokémon found with type {type_name}"}
        
        return {
            "type": type_name,
            "count": len(type_pokemon),
            "pokemon": type_pokemon['Name'].tolist()
        }
    
    def get_pokemon_by_generation(self, gen_num: int) -> Dict[str, Any]:
        """Get all Pokémon from a specific generation."""
        gen_pokemon = self.pokemon_df[self.pokemon_df['Generation'] == gen_num]
        
        if len(gen_pokemon) == 0:
            return {"error": f"No Pokémon found in generation {gen_num}"}
        
        return {
            "generation": gen_num,
            "count": len(gen_pokemon),
            "pokemon": gen_pokemon['Name'].tolist()
        }
    
    def get_pokemon_moves(self, pokemon_name: str) -> Dict[str, Any]:
        """Get moves for a specific Pokémon."""
        # In a real implementation, this would query a moves database
        # For simplicity, we're returning placeholder data
        return {
            "pokemon": pokemon_name,
            "moves": ["Tackle", "Growl", "Ember", "Scratch"]  # Placeholder
        }
    
    def get_all_pokemon_names(self) -> List[str]:
        """Get a list of all Pokémon names."""
        return self.pokemon_df['Name'].tolist()

# Example usage
if __name__ == "__main__":
    data_system = PokemonDataSystem()
    result = data_system.query_pokemon("What is Pikachu?")
    print(result)
