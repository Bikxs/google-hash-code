from random import choice

from inputs import *

OUTPUT_FOLDER = 'output'


class Delivery:
    def __init__(self, team: Team, pizzas: List[Pizza]):
        self.team = team
        self.pizzas = pizzas
        if len(pizzas) != team.size:
            self.value = 0
        else:
            ingredients = []
            for pizza in pizzas:
                ingredients.extend(pizza.ingredients)
            self.value = len(set(ingredients))

    def __str__(self):
        pizzas_list = ' '.join([str(pizza.index) for pizza in self.pizzas])
        return f'{self.team.size} {pizzas_list}'


Genome = List[Delivery]


def get_value(genome: Genome) -> int:
    return sum([delivery.value for delivery in genome])


def generate_genome(problem: Problem) -> Genome:
    genome = []
    # pick pizzas randomly sending to teams
    pizzas = list(problem.pizzas)
    teams = list(problem.teams)

    # choose random team
    while pizzas and teams:
        team = choice(teams)
        teams.remove(team)
        team_pizzas = []

        # deliver randoms pizzas to team as long as they are available
        for x in range(team.size):
            pizza = choice(pizzas)
            team_pizzas.append(pizza)
            pizzas.remove(pizza)
            if len(pizzas) == 0:
                break
        genome.append(Delivery(team=team, pizzas=team_pizzas))

    return genome


def output_solution(name: Text, solution: Genome):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(random_solution)}\n")
        for _delivery in solution:
            the_file.write(f"{_delivery}\n")
    print(f'Solution saved {output_filename}')


if __name__ == '__main__':
    probs = problems()

    for problem in probs:
        print(f"Problem:{problem.filename}")
        print(f"\tPizzas:{problem.M}")
        print(f"\tTeams: {len(problem.teams)}")
        random_genome = generate_genome(problem)
        random_solution = [delivery for delivery in random_genome if delivery.value > 0]
        solution_value = sum([delivery.value for delivery in random_solution])
        print(f"\tSolution Value: {solution_value}")
        output_solution(problem.name, solution=random_solution)
