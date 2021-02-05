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

        self.teams = []
        self.team_sizes = []
        self.team_count = T2 + T3 + T4
        self.people = [x for x in range(T2 * 2 + T3 * 3 + T4 * 4)]
        team_number = 0
        for index, number in enumerate([T2, T3, T4]):
            for _ in range(number):
                self.teams.extend([team_number for _ in range(index + 2)])
                self.team_sizes.append(index + 2)
                team_number += 1
        self.people_count = len(self.people)
        self.pizza_count = len(self.pizzas)
        self.T2, self.T3, self.T4 = T2, T3, T4

    def __str__(self):
        return f'{self.filename}\n\tTeams:{self.T2}x2,{self.T3}x3,{self.T4}x4,\n\tPeople:{self.people_count}\n\tPizzas:{self.M}'


filenames = ['a_example',
             'b_little_bit_of_everything.in',
             'c_many_ingredients.in',
             'd_many_pizzas.in',
             'e_many_teams.in']

filenames = filenames[:3]


def problems() -> List[Problem]:
    return [Problem(filename) for filename in filenames]
