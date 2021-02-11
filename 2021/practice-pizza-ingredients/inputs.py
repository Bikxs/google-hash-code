from typing import List, Text

from utils import *


class Pizza:
    def __init__(self, id: int, number_of_ingredients: int, ingredients: List[Text]):
        self.id = id
        self.number_of_ingredients = number_of_ingredients
        self.ingredients = ingredients

    def __str__(self):
        return f'{self.id} {self.number_of_ingredients} {self.ingredients}'

    def __lt__(self, other):
        return len(self.ingredients) < len(other.ingredient_types)


class Team:
    def __init__(self, id: int, size: int):
        self.id = id
        self.size = size

    def __str__(self):
        return f'{self.id} T{self.size}'


class Problem:
    def __init__(self, filename: string):
        self.prefix = filename[0]
        self.filename = f"{INPUT_FOLDER}/{filename}"
        self.name = filename.replace(".in", "")
        """
        M ( 1 ≤ M ≤ 100000 ) - the number of pizzas available in the pizzeria
        T2 ( 0 ≤ T 2 ≤ 50000 ) - the number of 2-person teams
        T3 ( 0 ≤ T 3 ≤ 50000 ) - the number of 3-person teams
        T4 ( 0 ≤ T 4 ≤ 50000 ) - the number of 4-person teams
        """
        self.pizzas = []
        self.ingredient_types = list()
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
                    pizza = Pizza(id=i - 1, number_of_ingredients=number_of_ingredients, ingredients=ingredients)
                    self.pizzas.append(pizza)
                    self.ingredient_types.extend(ingredients)
                i += 1

        self.teams = []
        self.team_sizes = []
        self.team_count = T2 + T3 + T4
        self.people = [x for x in range(T2 * 2 + T3 * 3 + T4 * 4)]
        self.ingredient_types = set(self.ingredient_types)
        team_id = 0
        for size, number in [(2, T2), (3, T3), (4, T4)]:
            for _ in range(number):
                self.teams.append(Team(team_id, size))
                self.team_sizes.append(size)
                team_id += 1
        self.people_count = len(self.people)
        self.pizza_count = len(self.pizzas)
        self.T2, self.T3, self.T4 = T2, T3, T4

    def __str__(self):
        return f'{self.name.upper()}\n\tFilename: {self.filename}\n\tTeams: {self.T2:,}x2,{self.T3:,}x3,{self.T4:,}x4\n\t       = {self.team_count:,}\n\tPeople: {self.people_count:,}\n\tPizzas: {self.M:,}\n\tIngredients Types: {len(self.ingredient_types):,}'


def read_problem(filename) -> Problem:
    return Problem(filename)
