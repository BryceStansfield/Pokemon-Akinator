from enum import Enum
import numpy

class Calculator:
    """Tries to narrow down which pokemon you're thinking of by using the results of past questions and suggesting new ones"""
     
    def __init__(self, pokemon):
        """ Arguments:
        data (list of pokemon): Output from dataFunctions.load_data()"""
        self.pokemon = pokemon
        self.last_question = {"type":"None", "selection":"None"}    # What was the last question? Used for elimation

        ### Feature matrix construction ###
        ## Which pokemon can it still be?
        self.pokemon_viable = [True for i in range(0, len(pokemon))]

        ## Number of types
        self.num_types_found = False
        # Zeroth column == Does this pokemon have 1 type?, first column == Does this pokemon have two types?
        self.num_types_matrix = numpy.array([[len(mon["types"]) == i for mon in pokemon] for i in range(1,3)])

        ## Generics
        self.poke_types_list, self.poke_types_checked, self.poke_types_matrix = self.generic_matrix_constructor(["types", "type", "name"])              # Actual types
        self.poke_moves_list, self.poke_moves_checked, self.poke_moves_matrix = self.generic_matrix_constructor(["moves", "move", "name"])              # Moves
        self.poke_games_list, self.poke_games_checked, self.poke_games_matrix = self.generic_matrix_constructor(["game_indices", "version", "name"])   # Games
        return
        
    def generic_matrix_constructor(self, attributes):
        """Constructs generic matricies for use in the matrix initializer
        arguments:
        attributes (string[3]): We're grabbing self.pokemon[i][attributes[0]][j][attributes[1]][attributes[2]] for the construction of our matricies
        
        returns:
        att_list (list of strings): Gives the name of each attribute
        atts_checked (list of bools): Gives whether or not a given attribute value has been checked yet
        att_matrix (matrix): A matrix encoding which pokemon have which attributes. 1 = has, 0 = doesn't have"""
        # Where we're recording all of these attributes
        att_map = {}    # Stores which index each type has
        att_list = []   # Stores the name of each index's att
        atts_in_pokemon = []    # Used to construct the matrix

        # Looping over the attributes in the pokemon
        for mon in self.pokemon:
            temp_atts = []
            for att in mon[attributes[0]]:
                try:        # Do we already know about this attribute?
                    temp_atts.append(att_map[att[attributes[1]][attributes[2]]])
                except KeyError:
                    att_map[att[attributes[1]][attributes[2]]] = len(att_list)      # Adding this attribute to our map
                    temp_atts.append(len(att_list))                                 # What we wanted to do to begin with
                    att_list.append(att[attributes[1]][attributes[2]])              # Adding the name to our list
            atts_in_pokemon.append(temp_atts)
        atts_checked = [False for i in range(0, len(att_list))]    # Recording which of these atts have already been checked, used in solver code

        ## Matrix constructor
        # Initialization
        att_matrix = numpy.zeros([len(att_list),len(self.pokemon)])     

        # Filling the actual matrix:
        for i in range(0, len(self.pokemon)):
            for j in atts_in_pokemon[i]:
                att_matrix[j][i] = True
        
        # Returing everything we need
        return att_list, atts_checked, att_matrix

    def reset(self):
        """ Resets the calculator to its default state for a new game"""
        ## Resetting the state variables
        self.pokemon_viable = [True for i in range(0, len(self.pokemon))]    # Which pokemon are still possible?
        self.last_question = {"type":"None", "selection":"None"}    # What was the last question? Used for elimation
        self.num_types_found = False                                # Have we figured out how many types this pokemon has?
        
        # Checked variables
        for i in range(len(self.poke_moves_checked)):
            self.poke_moves_checked = False
        for i in range(len(self.poke_games_checked)):
            self.poke_games_checked = False
        for i in range(len(self.poke_types_checked)):
            self.poke_types_checked[i] = False
        
        return

    def maximize_generic_information(self, matrix, checked):
        """Maximizes the information gained by asking a question based on the passed in matrix
        arguments:
        matrix (matrix): A pokemon attribute matrix
        checked (list of bools): Which columns of the matrix have already been checked
        
        returns:
        percentage (float): Percentage of maximal information gained
        index (int): Index for the column of the matrix this refers to"""
        return

    def generate_question(self):
        """ Uses current information to ask a question
        
        returns:
        question (string): Human readable question string"""
        return