from enum import Enum
import numpy

AttMap = {
    "num_types": 0,
    "poke_types": 1,
    "poke_moves": 2,
    "poke_games": 3
}

class Calculator:
    """Tries to narrow down which pokemon you're thinking of by using the results of past questions and suggesting new ones"""
     
    def __init__(self, pokemon):
        """ Arguments:
        data (list of pokemon): Output from dataFunctions.load_data()"""
        self.pokemon = pokemon
        self.last_question = {"type":"None", "selection":"None"}    # What was the last question? Used for elimation

        ### Feature matrix construction ###
        self.features_exhausted = [False, False, False, False]      # Which features have already been used up?     

        ## Which pokemon can it still be?
        self.pokemon_viable = numpy.array([True for i in range(0, len(pokemon))])
        self.num_pokemon_viable = len(pokemon)

        ## Number of types
        # ith row == Does this pokemon have i types?
        self.num_types_matrix = numpy.array([[len(mon["types"]) == i for mon in pokemon] for i in range(0,3)])
        self.num_types_checked = [False, False, False]

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
        self.num_types_checked = [False, False]                                # Have we figured out how many types this pokemon has?
        
        # Checked variables
        for i in range(len(self.poke_moves_checked)):
            self.poke_moves_checked = False
        for i in range(len(self.poke_games_checked)):
            self.poke_games_checked = False
        for i in range(len(self.poke_types_checked)):
            self.poke_types_checked[i] = False
        
        # Exhausted features
        self.features_exhausted = [False, False, False, False]
        return

    def maximize_generic_information(self, matrix, checked):
        """Maximizes the information gained by asking a question based on the passed in matrix
        arguments:
        matrix (matrix): A pokemon attribute matrix
        checked (list of bools): Which columns of the matrix have already been checked
        
        returns:
        percentage (float): Percentage of maximal information gained
        index (int): Index for the column of the matrix this refers to"""

        # Have we already gotten all of the possible information from this matrix?
        if(all(checked)):
            return 0, -1
        
        # Otherwise, let's check the unchecked rows for the most information:
        best_info = 0
        best_index = -1
        for i in range(len(matrix)):
            if not checked[i]:
                # Information in this case is inversely proportional to the distance of num_true from self.num_pokemon_viable/2
                # E.g. how far it is from an optimal split
                num_true = sum(numpy.multiply(matrix[i], self.pokemon_viable))
                info = 1-abs(num_true-(self.num_pokemon_viable/2))/(self.num_pokemon_viable/2)

                # Did we get no info from this?
                if(info == 0):
                    checked[i] = 0  # If so, don't check it again

                # Otherwise, check if this is the best info so far:
                if(info > best_info):
                    best_info = info
                    best_index = i
        return best_info, best_index

    def generate_question(self):
        """ Uses current information to ask a question
        
        returns:
        end_state (bool): Is this the end of a game?
        question (string): Human readable question string"""
        
        # Can we even ask a question?
        if(sum(self.pokemon_viable) == 1):
            return True, "I've guessed your pokemon! It's: " + self.pokemon[self.pokemon_viable.tolist().index(1)]["species"]["name"]
        if(all(self.features_exhausted)):
            return True, "I can't guess your pokemon T_T"
        
        ### Ok, so let's try and ask a question then
        ## Figuring out how much information we can gleen from each matrix

        # What do we have to run to evaluate information for our attributes? Order: Poke_types, Poke_moves, Poke_games
        information_functions = [lambda: self.maximize_generic_information(self.num_types_matrix, self.num_types_checked),
                                lambda: self.maximize_generic_information(self.poke_types_matrix, self.poke_types_checked),
                                lambda: self.maximize_generic_information(self.poke_moves_matrix, self.poke_moves_checked),
                                lambda: self.maximize_generic_information(self.poke_games_matrix, self.poke_games_checked)]
        should_run = [not self.features_exhausted[AttMap["num_types"]],
                      not self.features_exhausted[AttMap["poke_types"]],
                      not self.features_exhausted[AttMap["poke_moves"]],
                      not self.features_exhausted[AttMap["poke_games"]]]      # Do we even bother to run this?
        
        # Running every information function that isn't exhausted, and keeping track of which is best
        print(sum(self.pokemon_viable))
        best_info = 0
        best_index = -1
        best_i = -1
        for i in range(0, 4):
            if should_run[i]:
                information, index = information_functions[i]()
                if information > best_info:
                    print(i, information, best_index, best_info)
                    best_info = information
                    best_index = index
                    best_i = i
                elif information == 0:      # If we get zero information, that means this feature is exhaused
                    self.features_exhausted[i] = True
        
        ### Returning a question
        ## Turns out everything was exhausted T_T
        if best_info == 0:
            return True, "I can't guess your pokemon T_T"

        ## Otherwise, choose a question, give it to the player, and record the question
        self.last_question = {"type": best_i, "selection": best_index}

        # Annoying if/else tree for question
        if best_i == AttMap["num_types"]:         # Num types matrix
            return False, "Does your pokemon have exactly " + str(best_index) + " types?"
        elif best_i == AttMap["poke_types"]:       # Poke types matrix
            return False, "Does your pokemon have the type: " + self.poke_types_list[best_index]
        elif best_i == AttMap["poke_moves"]:       # Poke moves matrix
            return False, "Can your pokemon learn the move: " + self.poke_moves_list[best_index]
        else:                   # Poke games matrix
            return False, "Is your pokemon in: " + self.poke_games_list[best_index]
        return

    def generic_resolver(self, matrix, index, answer):
        """Updates self.pokemon_viable given an information index, an index, and an answer for whether or not that index is true
        NOTE TO SELF: Does this need to be a function?
        arguments:
        matrix (matrix): a pokemon attribute matrix
        index (int): a row index to query in this matrix
        answer (-1, 0, 1): Is this attribute in the pokemon?: -1 -> false; 0 -> indeterminate; 1-> true"""
        # Edge condition
        if answer == 0:
            return
        # We just loop through this row, and set pokemon_viable accordingly
        if answer == 1:
            self.pokemon_viable = numpy.multiply(self.pokemon_viable, matrix[index])
        elif answer == -1:
            self.pokemon_viable = numpy.multiply(self.pokemon_viable, numpy.logical_not(matrix[index]))
        self.num_pokemon_viable = sum(self.pokemon_viable)
        return


    def resolve_question(self, answer):
        """ Inputs the answer to the last question, and performs neccessary computations.
        Arguments:
        answer (-1, 0, 1): Answer to the last question: -1 -> false; 0 -> indeterminate; 1-> true"""
        ## Dealing with the individual "checked" variables and resolving the matrix's consequences
        # A big if/else block
        if self.last_question["type"] == AttMap["num_types"]:       # Num types matrix
            self.num_types_checked[self.last_question["selection"]] = True
            self.generic_resolver(self.num_types_matrix,self.last_question["selection"], answer)
        elif self.last_question["type"] == AttMap["poke_types"]:     # Poke types matrix
            self.poke_types_checked[self.last_question["selection"]] = True
            self.generic_resolver(self.poke_types_matrix,self.last_question["selection"], answer)
        elif self.last_question["type"] == AttMap["poke_moves"]:     # Poke moves matrix
            self.poke_moves_checked[self.last_question["selection"]] = True
            self.generic_resolver(self.poke_moves_matrix,self.last_question["selection"], answer)
        else:                           # Poke games matrix
            self.poke_games_checked[self.last_question["selection"]] = True
            self.generic_resolver(self.poke_games_matrix,self.last_question["selection"], answer)
        
        return