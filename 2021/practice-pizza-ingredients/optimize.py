import re
import sys
from random import choice, sample

import matplotlib.pyplot as plt
import numpy as np

from inputs import *
from utils import *


def plot(name, logs):
    # Genetic Algorithm is done - extract statistics:
    df_logs = pd.DataFrame(logs)
    df_logs.set_index('generation')
    df_logs = df_logs[['min', 'max', 'mean']]
    ax = df_logs.plot(title=f'{name}\nFitness over Generations', xlabel='Generation', ylabel='Fitness')
    ax.legend(loc='best')
    plt.show()


def fitness_function(individual: pd.DataFrame) -> int:
    return individual['value'].sum()


# helper function to swap pizzas between teams
def swap_pizzas(df_1, index1, index2, df_2=None):
    if df_2 is None:
        df_2 = df_1

    pizzas_1, pizzas_2 = df_1['pizza_ids'].iloc[index1].copy(), df_2['pizza_ids'].iloc[index2].copy()

    pizza_1 = choice(pizzas_1)
    pizzas_1.remove(pizza_1)

    pizza_2 = choice(pizzas_2)
    pizzas_2.remove(pizza_2)

    if pizza_2 in pizzas_1:
        return
    if pizza_1 in pizzas_2:
        return

    pizzas_1.append(pizza_2)
    pizzas_2.append(pizza_1)
    if len(set(pizzas_2) - set(pizzas_1)) >0:
        return
    df_1['pizza_ids'].iloc[index1] = pizzas_1
    df_1['pizza_ids_sum'].iloc[index1] = sum(pizzas_1)
    df_2['pizza_ids'].iloc[index2] = pizzas_2
    df_2['pizza_ids_sum'].iloc[index2] = sum(pizzas_2)

    ingredients1, ingredients2 = [], []
    for pizza in pizzas_1:
        ingredients1.extend(pizzas[pizza])
    for pizza in pizzas_2:
        ingredients2.extend(pizzas[pizza])
    value_1 = len(set(ingredients1)) ** 2
    value_2 = len(set(ingredients2)) ** 2
    df_1['value'].iloc[index1] = value_1
    df_2['value'].iloc[index2] = value_2


def mutate(ind: pd.DataFrame, mutation_probability=0.1) -> pd.DataFrame:
    indices = ind.index.values.tolist()
    for index in indices:
        if np.random.random() <= mutation_probability:
            index2 = choice(indices)
            if index == index2:
                continue
            swap_pizzas(ind, index, index2)

    return ind


def crossover_cycle(ind1: pd.DataFrame, ind2: pd.DataFrame) -> List[pd.DataFrame]:
    child1 = ind1.copy(deep=True)
    child2 = ind1.copy(deep=True)
    child3 = ind2.copy(deep=True)
    child4 = ind2.copy(deep=True)

    team_swaps = min(len(ind1), len(ind2))
    for i in range(team_swaps):
        swap_pizzas(child1, i, i, child3)
        swap_pizzas(child2, i, i, child4)
    children = [child1, child2, child3, child4]
    return [(child['value'].sum(), child) for child in children]


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


POPULATION_SIZE = 10
N_MATINGS = 40
N_GENERATIONS = 100
ELITE_POPULATION_TO_SAVE = POPULATION_SIZE/10
MUTATION_PROBABILITY = .10
pd.options.mode.chained_assignment = None
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Provide arguments - Folder Name")
        exit(0)
    folder_name = sys.argv[1]
    if (len(sys.argv) >= 3):
        N_GENERATIONS = int(sys.argv[1])
    folder = f'{INTERMEDIATE_FOLDER}/{folder_name}'
    if not os.path.exists(folder):
        print(f"Folder '{folder}' does not exist")
        exit(0)
    files = os.listdir(folder)
    if not files:
        print(f"No files found in folder '{folder}'")
        exit(0)
    population = []
    for file in files:
        # extract the points
        m = re.search('-(.+?).csv', file)
        if m:
            pts, df = load_deliveries(f'{folder}/{file}')
            population.append((pts, df))
        else:
            continue
    if len(population) < POPULATION_SIZE:
        print(f"Not enough individuals (files) in '{folder}'.\n Population of at least {POPULATION_SIZE} is needed")
        exit(0)
    population.sort(reverse=True, key=lambda x: x[0])

    problem = read_problem(f"{folder_name}.in")
    pizzas = {pizza.id: pizza.ingredients for pizza in problem.pizzas}

    logs = []
    for generation in range(0, N_GENERATIONS):
        ## select
        population = population[:POPULATION_SIZE]
        ## crossovers
        for _ in range(0, N_MATINGS):
            items_to_mate = sample(population, k=2)
            offspring = crossover_cycle(items_to_mate[0][1], items_to_mate[1][1])
            population.extend(offspring)

        ## mutates
        for fitness, individual in population:
            mutate(individual, MUTATION_PROBABILITY)

        population.sort(reverse=True, key=lambda x: x[0])

        fitnesses = np.array([fitness for fitness, individual in population])
        population = population[:POPULATION_SIZE]
        # gen_number,min,max, mean,std
        logs.append(
            {'generation': generation, 'min': np.min(fitnesses), 'max': np.max(fitnesses), 'mean': np.mean(fitnesses),
             'std': np.std(fitnesses)})
        # save top X members of population
        for points, individual in population[:ELITE_POPULATION_TO_SAVE]:
            filename, points, new_file = save_deliveries_dataframe(problem_prefix=folder_name.lower()[0],
                                                                   folder=folder,
                                                                   df_deliveries=individual)
            if new_file:
                print(f"\t{folder_name}: New Optimized output!! {filename}:{points:,}")

    plot(folder_name, logs)
