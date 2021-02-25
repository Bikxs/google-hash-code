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
    intersection = set(pizzas_1).intersection(set(pizzas_2))
    selection_1 = list(set(pizzas_1) - intersection)
    selection_2 = list(set(pizzas_2) - intersection)
    if not selection_1:
        return
    if not selection_2:
        return
    pizza_1 = choice(selection_1)
    pizzas_1.remove(pizza_1)

    pizza_2 = choice(selection_2)
    pizzas_2.remove(pizza_2)

    pizzas_1.append(pizza_2)
    pizzas_2.append(pizza_1)
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
    children_number = 20
    children_a = [ind1.copy(deep=True) for _ in range(children_number)]
    children_b = [ind2.copy(deep=True) for _ in range(children_number)]

    team_swaps = min(len(ind1), len(ind2))

    for ch_num in range(children_number):
        indices_1 = sample(children_a[ch_num].index.values.tolist(), team_swaps)
        indices_2 = sample(children_b[ch_num].index.values.tolist(), team_swaps)
        for i in range(team_swaps):
            swap_pizzas(children_a[ch_num], indices_1[i], indices_2[i], children_b[ch_num])

    children = children_a + children_b
    return pd.DataFrame([(child['value'].sum(), child) for child in children], columns=['value', 'df'])


POPULATION_SIZE = 100
N_MATINGS = 40
N_GENERATIONS = 100
ELITE_POPULATION_TO_SAVE = int(POPULATION_SIZE / 5)
MUTATION_PROBABILITY = .10
pd.options.mode.chained_assignment = None
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Provide arguments - Folder Name")
        exit(0)
    folder_name = sys.argv[1]
    if (len(sys.argv) >= 3):
        POPULATION_SIZE = int(sys.argv[2])
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
        print(
            f"Not enough individuals (files) in '{folder}'.\n Population of at least {POPULATION_SIZE} is needed, but {len(population)} found")
        exit(0)
    population = pd.DataFrame(population, columns=['value', 'df'])

    problem = read_problem(f"{folder_name}.in")
    pizzas = {pizza.id: pizza.ingredients for pizza in problem.pizzas}

    logs = []
    for generation in range(0, N_GENERATIONS):
        ## select -
        population = population.sample(n=POPULATION_SIZE, weights='value')
        population.sort_values(['value'], ascending=[False], inplace=True)
        # population.reset_index(inplace=True, drop=True)
        # print(population.head(10))
        ## crossovers
        for _ in range(0, N_MATINGS):
            items_to_mate = population.sample(n=2)
            offspring = crossover_cycle(items_to_mate['df'].iloc[0], items_to_mate['df'].iloc[1])
            population.append(offspring, ignore_index=True)
        population.reset_index(inplace=True, drop=True)

        ## mutates
        for index in population.index.values:
            individual = population['df'].iloc[index]
            mutate(individual, MUTATION_PROBABILITY)

        population.sort_values(['value'], ascending=[False], inplace=True)
        fitnesses = population['value'].tolist()
        # population = population[:POPULATION_SIZE]
        # gen_number,min,max, mean,std
        logs.append(
            {'generation': generation, 'min': np.min(fitnesses), 'max': np.max(fitnesses), 'mean': np.mean(fitnesses),
             'std': np.std(fitnesses)})
        # print(population.head(10))
        # save top X members of population
        for row in population[:ELITE_POPULATION_TO_SAVE].index.values:
            individual = population['df'].iloc[row]
            filename, points, new_file = save_schedules_dataframe(problem_prefix=folder_name.lower()[0],
                                                                  folder=folder,
                                                                  df_schedules=individual)
            if new_file:
                print(f"\t{folder_name.upper()}: New Optimized output!! {filename}:{points:,}")

    plot(folder_name, logs)
