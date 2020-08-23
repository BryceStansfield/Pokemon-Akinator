import requests
import os
import pickle
import json

def load_data(backup_address):
    """Returns array of loaded pokemon dictionaries; If a local backup exists, then that's loaded. Otherwise we load from pokeapi and save to a local backup.
    Arguments:
    backup_address (str): File system address of your local backup"""
    # We need a file path, don't want to DOS pokepath by accident
    if(backup_address.strip() == ""):   # This is the best I can quickly figure out
        raise Exception("You must supply a backup_address")
    
    # Does a backup already exist?
    if(os.path.exists(backup_address)):
        return pickle.load(open(backup_address, "rb"))

    # Otherwise, let's load it from the pokeapi
    list_request = requests.get("https://pokeapi.co/api/v2/pokemon",
                                params={"limit":"10000"})

    # Did the request work?
    list_request.raise_for_status()
    
    
    # Now, using this information to populate a list of pokemon objects
    list_of_pokemon = json.loads(list_request.text)
    pokemon = []
    # NOTE: This is PURPOSEFULLY syncronous. I don't feel comfortable sending requests to pokeapi faster
    # Think of this as an easy way of rate limiting yourself.
    for mon in list_of_pokemon["results"]:      
        url = mon["url"]     # The pokeapi url for this pokemon
        print(url)
        # Grabbing that url
        mon_request = requests.get(url)
        mon_request.raise_for_status()
        
        # Decoding it, and adding it to the array
        pokemon.append(json.loads(mon_request.text))
    
    # Adding this pokemon list to the backup
    pickle.dump(pokemon, open(backup_address, "wb"))
    return pokemon