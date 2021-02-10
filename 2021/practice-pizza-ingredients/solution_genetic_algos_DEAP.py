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
        self.ingredients = []
        if len(pizzas) != team_size:
            self.value = 0
        else:
            for pizza in pizzas:
                self.ingredients.extend(pizza.ingredients)
            self.value = len(set(self.ingredients)) ** 2
            """For each delivery, the delivery score is the square of the total number of different ingredient_types of
            all the pizzas in the delivery
            """
        self.pizza_indices = [pizza.id for pizza in self.pizzas]

    def __str__(self):
        pizzas_list = ' '.join([str(pizza_index) for pizza_index in self.pizza_indices])
        return f'{self.team_size} {pizzas_list}'


def output_solution(name: Text, deliveries: List[Delivery]):
    deliveries = [delivery for delivery in deliveries if delivery.team_size == len(delivery.pizzas)]
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

import multiprocessing


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


def divide_chunks(list, chunk_size):
    # https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    # looping till length list
    for i in range(0, len(list), chunk_size):
        yield list[i:i + chunk_size]


def generate_genome(ind_cls):
    all_pizzas = [x for x in range(problem.pizza_count)]
    pizzas = problem.pizzas
    """
    if np.random.random() < .3:

        current = choice(pizzas)
        choosen = [current]
        for x in range(num_genes):
            unchossen = [pizza for pizza in pizzas if pizza not in choosen]
            if len(unchossen) == 0:
                break
            if chunk_size < len(unchossen):
                sampled = sample(unchossen, chunk_size)
            else:
                sampled = unchossen
            matches = [
                (pizza_differences(current.ingredient_types, sampled_pizza.ingredient_types), sampled_pizza)
                for sampled_pizza in sampled]
            current = matches[0][1]
            choosen.append(current)
        # assert len(choosen) == num_genes
        return ind_cls([pizza.id for pizza in choosen])
    """
    if np.random.random() < .3:
        # generate genome the smart way

        vec = [pizza.id for pizza in pizzas]
        ingedients = [len(pizza.ingredient_types) for pizza in pizzas]
        p = np.array(ingedients) / sum(ingedients)
        return ind_cls(np.random.choice(vec, num_genes, replace=False, p=p).tolist())
    else:
        return ind_cls(sample(all_pizzas, num_genes))


def deliveries_from_individual(individual):
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
    deliveries = deliveries_from_individual(individual)
    return sum(delivery.value for delivery in deliveries),


def mutSwapOptimize(individual, indpb, cls_img):
    """Shuffle the attributes of the input individual and return the mutant.
    The *individual* is expected to be a :term:`sequence`. The *indpb* argument is the
    probability of each attribute to be moved. Usually this mutation is applied on
    vector of indices.

    This function then optimizes the individual groupings as per pizza problem

    :param individual: Individual to be mutated.
    :param indpb: Independent probability for each attribute to be exchanged to
                  another position.
    :returns: A tuple of one individual.
    """
    size = len(individual)
    for i in range(size):
        if np.random.random() < indpb:
            swap_indx = np.random.randint(0, size)
            if swap_indx == i:
                pass
            else:
                temp_val = individual[i]
                individual[i] = individual[swap_indx]
                individual[swap_indx] = temp_val
    if np.random.random() < 0.8:
        return cls_img(individual),
    # optimizaing
    deliveries = deliveries_from_individual(individual)
    chunks = divide_chunks(deliveries, chunk_size=chunk_size)
    # let optimized every 10 deliveries
    new_individual = []
    for chunk in chunks:
        for delivery in optimize_deliveries(chunk):
            new_individual.extend(delivery.pizza_indices)

    return cls_img(new_individual),


def pizza_differences(ingredients1, ingredients2):
    return len(set(ingredients1 + ingredients2))


def optimize_deliveries(deliveries: List[Delivery]) -> List[Delivery]:
    # collect all pizzas
    pizzas = {}
    for delivery in deliveries:
        for pizza in delivery.pizzas:
            pizzas[pizza.id] = pizza

    new_deliveries = []
    # assign_pizzas into deliveries
    for delivery in deliveries:
        new_delivery_pizzas = []
        pizza_id = np.random.choice([x for x in pizzas.keys()])
        new_pizza = pizzas[pizza_id]
        del pizzas[pizza_id]

        new_delivery_pizzas.append(new_pizza)
        new_delivery_pizzas_ingredients = new_pizza.ingredients.copy()
        for _ in range(len(delivery.pizzas) - 1):
            matches = [
                (pizza_differences(new_delivery_pizzas_ingredients, remaining_pizza.ingredients), key)
                for key, remaining_pizza in pizzas.items()]
            matches.sort(reverse=True)
            pizza_id = matches[0][1]
            new_pizza = pizzas[pizza_id]
            del pizzas[pizza_id]

            new_delivery_pizzas.append(new_pizza)
            new_delivery_pizzas_ingredients.extend(new_pizza.ingredients.copy())
        new_delivery = Delivery(delivery.team_size, new_delivery_pizzas)
        new_deliveries.append(new_delivery)
    return new_deliveries


def cxCycle(ind1, ind2):
    cycle_1 = list()
    cycle_2 = list()
    idx = 0

    _ind1_set, _ind2_set = set(ind1), set(ind2)
    intersection = list(_ind1_set & _ind2_set)
    index_mappings = {index: ind1.id(value) for index, value in enumerate(ind2) if value in intersection}
    in_ind1_not_in_ind2 = list(_ind1_set - _ind2_set)
    in_ind2_not_in_ind1 = list(_ind2_set - _ind1_set)
    np.random.shuffle(in_ind2_not_in_ind1)
    differences = list(zip(in_ind1_not_in_ind2, in_ind2_not_in_ind1))
    index_mappings.update({ind2.id(b): ind1.id(a) for a, b in differences})
    # pprint(index_mappings)
    while 1:
        if idx in cycle_1:
            break
        cycle_1.append(idx)
        idx = index_mappings[idx]
    left = [i for i in range(len(ind2)) if i not in cycle_1]
    if len(left) != 0:
        start = min(left)
    else:
        return ind1, ind2
    idx = start
    while 1:
        if idx in cycle_2:
            break
        cycle_2.append(idx)
        idx = index_mappings[idx]
    for i in cycle_2:
        temp = ind2[i]
        ind2[i] = ind1[i]
        ind1[i] = temp
    return ind1, ind2


toolbox = base.Toolbox()

if __name__ == '__main__':

    make_code_zip(OUTPUT_FOLDER)
    print()
    problems_meta = {'a': {'filename': 'a_example',
                           'max_generations': 3,
                           'population_size': 10,
                           'chunk_size': 10},
                     'b': {'filename': 'b_little_bit_of_everything.in',
                           'max_generations': 50,
                           'population_size': 200,
                           'chunk_size': 40},
                     'c': {'filename': 'c_many_ingredients.in',
                           'max_generations': 50,
                           'population_size': 100,
                           'chunk_size': 500},
                     'd': {'filename': 'd_many_pizzas.in',
                           'max_generations': 50,
                           'population_size': 60,
                           'chunk_size': 200},
                     'e': {'filename': 'e_many_teams.in',
                           'max_generations': 50,
                           'population_size': 50,
                           'chunk_size': 400}}

    for key, problem_meta in problems_meta.items():
        if not key in ['b', 'c', 'd', 'e']:
            continue
        problem = read_problem(problem_meta['filename'])

        print()
        print(problem)
        NGEN = problem_meta['max_generations']
        MU = problem_meta['population_size']
        LAMBDA = MU * 2
        CXPB = 0.1
        MUTPB = 0.7
        chunk_size = problem_meta['chunk_size']
        print(f"Population size: {MU}")
        num_genes = min(problem.people_count, problem.pizza_count)

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        pool = multiprocessing.Pool()
        toolbox.register("map", pool.map)
        # Structure initializers
        toolbox.register("individual", generate_genome, creator.Individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", fitness_function)
        # toolbox.register("mate", tools.cxUniformPartialyMatched, indpb=0.5)
        toolbox.register("mate", cxCycle)
        toolbox.register("mutate", mutSwapOptimize, indpb=0.3, cls_img=creator.Individual)
        toolbox.register("select", tools.selSPEA2)

        # toolbox.register("select", tools.selRoulette)

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
        solution = deliveries_from_individual(best_ind)
        output_solution(name=problem.name, deliveries=solution)
        # plot chart
        plot(problem.name, logbook=logbook)
        # save population
