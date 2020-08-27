import dataFunctions
from Calculator import Calculator

def setup(file_directory):
    return Calculator(dataFunctions.load_data(file_directory))


def answer_question(calculator):
    pass

def request_question(calculator):
    pass

if __name__ == "__main__":
    # Getting required info from the player
    file_directory = input("What is the directory of your save file?: ")
    
    # Grabbing the data and setting up the calculations
    calculator = setup(file_directory)

    # Running the actual game
    while True:
        done, question = calculator.generate_question()
        print(question)
        if done:
            break
        answer = int(input("Is this true (1), false (-1) or are you unsure (0)?: "))
        calculator.resolve_question(answer)