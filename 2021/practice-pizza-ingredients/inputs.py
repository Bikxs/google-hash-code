import string
from typing import List, Text

INPUT_FOLDER = 'input-data'


class Pizza:
    def __init__(self, index: int, number_of_ingredients: int, ingredients: List[Text]):
        self.index = index
        self.number_of_ingredients = number_of_ingredients
        self.ingredients = ingredients

    def __str__(self):
        return f'{self.index} {self.number_of_ingredients} {self.ingredients}'


class Team:
    def __init__(self, size: int):
        self.size = size

    def __str__(self):
        return f'T{self.size}'


class Problem:
    def __init__(self, filename: string):
        self.filename = f"{INPUT_FOLDER}/{filename}"
        self.name = filename.replace(".in", "")
        """
        M ( 1 ≤ M ≤ 100000 ) - the number of pizzas available in the pizzeria
        T2 ( 0 ≤ T 2 ≤ 50000 ) - the number of 2-person teams
        T3 ( 0 ≤ T 3 ≤ 50000 ) - the number of 3-person teams
        T4 ( 0 ≤ T 4 ≤ 50000 ) - the number of 4-person teams
        """
        self.pizzas = []
        i = 0
        with open(self.filename, 'r') as f:
            for line in f:
                line_data = line.strip().split(' ')
                if i == 0:
                    self.M = int(line_data[0])  # the number of pizzas available in the pizzeria
                    T2 = int(line_data[1])  # the number of 2-person teams
                    T3 = int(line_data[2])  # the number of 3-person teams
                    T4 = int(line_data[3])  # the number of 4-person teams
                else:
                    number_of_ingredients = int(line_data[0])
                    ingredients = list(line_data[1:])
                    ingredients.sort()
                    pizza = Pizza(index=i - 1, number_of_ingredients=number_of_ingredients, ingredients=ingredients)
                    self.pizzas.append(pizza)
                i += 1
        self.teams = [Team(2) for x in range(T2)] + [Team(3) for x in range(T3)] + [Team(4) for x in range(T4)]

    def __str__(self):
        return f'{self.filename}\n\tTeams:{self.teams[0]}x2,{self.teams[1]}x3,{self.teams[2]}x4, Pizzas:{self.M}'


filenames = ['a_example',
             'b_little_bit_of_everything.in',
             'c_many_ingredients.in',
             'd_many_pizzas.in',
             'e_many_teams.in']


def problems() -> List[Problem]:
    return [Problem(filename) for filename in filenames]
