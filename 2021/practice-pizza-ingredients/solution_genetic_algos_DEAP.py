import warnings
from random import sample

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

from code_utils import make_code_zip
from inputs import *

OUTPUT_FOLDER = 'output'


class Delivery:
    def __init__(self, team_size: int, pizzas: List[Pizza]):
        self.team_size = team_size
        self.pizzas = [pizza for pizza in pizzas if pizzas != -1]
        if len(pizzas) != team_size:
            self.value = 0
        else:
            ingredients = []
            for pizza in pizzas:
                ingredients.extend(pizza.ingredients)
            self.value = len(set(ingredients)) ** 2
            """For each delivery, the delivery score is the square of the total number of different ingredients of
            all the pizzas in the delivery
            """

    def __str__(self):
        pizzas_list = ' '.join([str(pizza.index) for pizza in self.pizzas])
        return f'{self.team_size} {pizzas_list}'


Genome = List[Delivery]


def output_solution(name: Text, deliveries: Genome):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(deliveries)}\n")
        for _delivery in deliveries:
            the_file.write(f"{_delivery}\n")
    print(f'Solution saved {output_filename}')


from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import matplotlib.pyplot as plt


def plot(name, logbook):
    # Genetic Algorithm is done - extract statistics:
    max, avg, min = logbook.select("max", "avg", "min")

    # plot statistics:
    plt.figure()
    ax = plt.subplot()

    ax.plot(min, color='red', label='min')
    ax.plot(avg, color='blue', label='avg')
    ax.plot(max, color='green', label='max')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(f'{name}\nFitness over Generations')
    ax.legend(loc='best')
    plt.show()


if __name__ == '__main__':
    make_code_zip(OUTPUT_FOLDER)
    print()
    problems_meta = {'a': {'filename': 'a_example', 'max_generations': 20, 'population_size': 20},
                     'b': {'filename': 'b_little_bit_of_everything.in', 'max_generations': 100, 'population_size': 50},
                     'c': {'filename': 'c_many_ingredients.in', 'max_generations': 200, 'population_size': 100},
                     'd': {'filename': 'd_many_pizzas.in', 'max_generations': 300, 'population_size': 100},
                     'e': {'filename': 'e_many_teams.in', 'max_generations': 400, 'population_size': 100}}

    for problem_meta in problems_meta.values():
        problem = read_problem(problem_meta['filename'])

        print()
        print(problem)
        NGEN = problem_meta['max_generations']
        MU = problem_meta['population_size']
        LAMBDA = MU * 2
        CXPB = 0.7
        MUTPB = 0.2
        print(f"Population size: {MU}")
        num_genes = min(problem.people_count, problem.pizza_count)


        def generate_genome(ind_cls) -> Genome:
            all_pizzas = [x for x in range(problem.pizza_count)]
            return ind_cls(sample(all_pizzas, num_genes))


        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        # Structure initializers
        toolbox.register("individual", generate_genome, creator.Individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)


        def solution_from_ind(individual):
            people = problem.people[:num_genes]
            teams = problem.teams[:num_genes]

            data = pd.DataFrame(data={'people': people, 'teams': teams,
                                      'pizzas': individual}).set_index(
                'people')
            group = data.groupby(['teams']).agg(list)
            deliveries = []
            for team_number, row in group.iterrows():
                team_size = problem.team_sizes[team_number]
                team_pizzas = [problem.pizzas[int(pizza_number)] for pizza_number in row['pizzas'] if
                               pizza_number != -1]
                deliveries.append(Delivery(team_size, team_pizzas))
            return deliveries


        def fitness_function(individual):
            deliveries = solution_from_ind(individual)
            return sum(delivery.value for delivery in deliveries),


        toolbox.register("evaluate", fitness_function)
        toolbox.register("mate", tools.cxUniformPartialyMatched, indpb=0.5)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.3)
        toolbox.register("select", tools.selTournament, tournsize=3)

        pop = toolbox.population(n=MU)
        hof = tools.ParetoFront()
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        # stats = tools.Statistics(lambda ind:fitness_function(ind))
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                                                 halloffame=hof)
        # print(hof)
        # print(stats)
        best_ind = tools.selBest(hof, 1)[0]
        print(f"\tBest Individual: {best_ind}")
        solution = solution_from_ind(best_ind)
        output_solution(name=problem.name, deliveries=solution)
        # plot chart
        plot(problem.name, logbook=logbook)
        # save population
