import sys
import warnings

import numpy as np

from inputs import *
from utils import *

warnings.filterwarnings("ignore")


def print_df_head(title: string, df: pd.DataFrame, rows=5):
    print("----------------------------------------------------------------------------")
    print(title)
    print("----------------------------------------------------------------------------")
    print(df.head(rows))
    print()


def strategy_sorting_looping(POOL_SIZE=None):
    df_pizzas_pool = df_pizzas[df_pizzas['delivered'] == False]
    strat_selected_pizzas = []
    strat_selected_ingredients = []
    start_pizza = 0
    limit = 0
    while len(strat_selected_pizzas) < team_size:
        for x in range(start_pizza, team_size):
            strat_selected_ingredients_num = len(strat_selected_ingredients)
            strat_selected_ingredients_num_unique = set(strat_selected_ingredients)

            def calculate_diffence(ingredients):
                # rem1 = pool_ingedients - set(selected_ingredients)
                return len(strat_selected_ingredients_num_unique - set(ingredients))

            for row in range(len(df_pizzas_pool)):
                if strat_selected_ingredients_num - calculate_diffence(
                        df_pizzas_pool['ingredients'].iloc[row]) <= limit:
                    selected_pizza = df_pizzas_pool.index.values[0]
                    strat_selected_pizzas.append(selected_pizza)
                    strat_selected_ingredients.extend(df_pizzas_pool['ingredients'].iloc[0])
                    break
        limit += 1
    strat_selected_pizzas.sort()

    strat_selected_ingredients = set(strat_selected_ingredients)
    return strat_selected_pizzas, strat_selected_ingredients


def strategy_sample_pooling_sorting(POOL_SIZE=100):
    first_pizza_choosen_randomly = False
    # pick random pizzas
    pool_size = min(remaining_pizzas, POOL_SIZE)

    df_pizzas_pool = df_pizzas[df_pizzas['delivered'] == False].sample(n=pool_size, replace=False)
    if first_pizza_choosen_randomly:
        # first pizza choosen randomly
        df_first_pizza = df_pizzas_pool.sample(n=1, replace=False)
        strat_selected_pizzas = [df_first_pizza.index.values[0]]
        strat_selected_ingredients = df_first_pizza['ingredients'].iloc[0].copy()
        start_pizza = 1
    else:
        strat_selected_pizzas = []
        strat_selected_ingredients = []
        start_pizza = 0
    for x in range(start_pizza, team_size):
        df_pizzas_pool = df_pizzas_pool[~df_pizzas_pool.index.isin(strat_selected_pizzas)]
        pool_ingedients = set(np.hstack(df_pizzas_pool['ingredients'].values)) - set(strat_selected_ingredients)

        def calculate_diffence(ingredients):
            # rem1 = pool_ingedients - set(selected_ingredients)
            return len(pool_ingedients - set(ingredients))

        df_pizzas_pool['difference'] = df_pizzas_pool['ingredients'].apply(calculate_diffence)

        df_pizzas_pool_selected = df_pizzas_pool[
            df_pizzas_pool['difference'] == df_pizzas_pool['difference'].min()]
        df_pizzas_pool_selected.sort_values(by=['num_ingredients', 'pizza_id'], ascending=[True, True],
                                            inplace=True)
        selected_pizza = df_pizzas_pool_selected.index.values[0]
        strat_selected_pizzas.append(selected_pizza)
        strat_selected_ingredients.extend(df_pizzas_pool_selected['ingredients'].iloc[0])

    strat_selected_pizzas.sort()

    strat_selected_ingredients = set(strat_selected_ingredients)
    return strat_selected_pizzas, strat_selected_ingredients


def strategy_sample_pooling_combinations(POOL_SIZE=20):
    # pick random pizzas
    pool_size = min(remaining_pizzas, POOL_SIZE)

    df_pizzas_pool = df_pizzas[df_pizzas['delivered'] == False].sample(n=pool_size, replace=False)

    from itertools import combinations
    delivery_combinations = list(combinations(df_pizzas_pool.index.values.copy(), team_size))
    pizzas_dict = df_pizzas_pool.T.to_dict()
    delivery_combinations_score = []

    def calculate_score(delivery_combination):
        ingredients = []
        for pizza in delivery_combination:
            ingredients.extend(pizzas_dict[pizza]['ingredients'])
        ingredients_count = len(ingredients)
        unique_ingredients_count = len(set(ingredients))
        return unique_ingredients_count - (ingredients_count - unique_ingredients_count)

    for delivery_combination in delivery_combinations:
        delivery_combinations_score.append((calculate_score(delivery_combination), delivery_combination))
    delivery_combinations_score.sort(reverse=True)
    best = delivery_combinations_score[0]
    strat_selected_pizzas = list(best[1])
    strat_selected_ingredients = []
    for pizza in strat_selected_pizzas:
        strat_selected_ingredients.extend(pizzas_dict[pizza]['ingredients'])
    strat_selected_ingredients = set(strat_selected_ingredients)
    strat_selected_pizzas.sort()

    strat_selected_ingredients = set(strat_selected_ingredients)
    return strat_selected_pizzas, strat_selected_ingredients


def strategy_random(POOL_SIZE=None):
    df_pizzas_pool = df_pizzas[df_pizzas['delivered'] == False].sample(n=team_size, replace=False)
    strat_selected_pizzas = df_pizzas_pool.index.values.copy()
    strat_selected_ingredients = set(np.hstack(df_pizzas_pool['ingredients'].values))
    strat_selected_pizzas.sort()
    strat_selected_ingredients = set(strat_selected_ingredients)
    return strat_selected_pizzas, strat_selected_ingredients


def pick_team():
    # pick random team
    # df_team = df_teams[df_teams['served'] == False].sample(n=1, replace=False)

    # pick team in order of size
    df_team = df_teams[df_teams['served'] == False]
    return df_team['size'].iloc[0], df_team['size'].iloc[0]


def pick_pizzas():
    # selected_pizzas, selected_ingredients = strategy_sample_pooling_combinations()
    # selected_pizzas, selected_ingredients = strategy_sample_pooling_combinations()
    # return strategy_sample_pooling_sorting(POOL_SIZE=1000)
    strategies = {'a_example': {'fn': strategy_sample_pooling_combinations, 'POOL_SIZE': 10},
                  'b_little_bit_of_everything': {'fn': strategy_sample_pooling_combinations, 'POOL_SIZE': 50},
                  'c_many_ingredients': {'fn': strategy_sample_pooling_combinations, 'POOL_SIZE': 30},
                  'd_many_pizzas': {'fn': strategy_sample_pooling_combinations, 'POOL_SIZE': 30},
                  'e_many_teams': {'fn': strategy_sample_pooling_combinations, 'POOL_SIZE': 30}}
    fn = strategies[problem.name]['fn']
    POOL_SIZE = strategies[problem.name]['POOL_SIZE']
    return fn(POOL_SIZE)


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print("Provide arguments - input_file_name and solutions_needed")
        exit(0)
    filename = sys.argv[1]
    individuals = int(sys.argv[2])
    problem = read_problem(filename)
    folder_name = f'{INTERMEDIATE_FOLDER}/{problem.name}/'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print()
    print(problem)
    print("\tGenerating deliveries....")
    print()

    for ind in range(individuals):
        # load data into pandas frame
        df_pizzas = pd.DataFrame(
            [{'pizza_id': pizza.id, 'num_ingredients': pizza.number_of_ingredients, 'ingredients': pizza.ingredients,
              'delivered': False} for
             pizza in problem.pizzas])
        df_pizzas.set_index('pizza_id', inplace=True)

        # sorting not need because of random sampling applied later
        df_pizzas.sort_values(['num_ingredients'], ascending=[0], inplace=True)

        # print_df_head("Pizzas", df_pizzas, 20)

        df_teams = pd.DataFrame(
            [{'team_id': team.id, 'size': team.size, 'served': False} for
             team in problem.teams])
        df_teams.set_index('team_id', inplace=True)
        df_teams.sort_values(['size', 'team_id'], ascending=[False, True], inplace=True)
        # print_df_head("Teams", df_teams, 20)

        # make deliveries
        deliveries = []
        delivery_id = 0
        remaining_pizzas = len(df_pizzas[df_pizzas['delivered'] == False])
        remaining_teams = len(
            df_teams.loc[(df_teams['served'] == False) & (df_teams['size'] <= remaining_pizzas), ['size']])
        skip_count = 0

        while remaining_teams > 0 and remaining_pizzas > 0:
            team_size, team_id = pick_team()
            if team_size > remaining_pizzas:
                if skip_count > 5:
                    # give up
                    break
                skip_count += 1
                continue
            skip_count = 0

            selected_pizzas, selected_ingredients = pick_pizzas()
            """ 
            For each delivery, the delivery score is the square of the total number of different ingredient_types of
            all the pizzas in the delivery
            """
            if len(selected_pizzas) == team_size:
                value = len(selected_ingredients) ** 2
            else:
                value = 0
            # update master records
            delivery = {'delivery_id': delivery_id,
                        'team_id': team_id,
                        'team_size': team_size,
                        'pizza_ids': selected_pizzas,
                        'pizza_ids_sum': sum(selected_pizzas),
                        'value': value}
            deliveries.append(delivery)

            df_teams.loc[df_teams.index.isin([team_id]), 'served'] = True
            df_pizzas.loc[df_pizzas.index.isin(selected_pizzas), 'delivered'] = True

            remaining_pizzas = len(df_pizzas[df_pizzas['delivered'] == False])
            remaining_teams = len(
                df_teams.loc[(df_teams['served'] == False) & (df_teams['size'] <= remaining_pizzas), ['size']])

            delivery_id += 1
        df_deliveries = pd.DataFrame(deliveries)
        df_deliveries.set_index('delivery_id', inplace=True)
        points = df_deliveries[df_deliveries['value'] > 0]['value'].sum()

        filename, points = save_deliveries_dataframe(problem.prefix, folder=folder_name, df_deliveries=df_deliveries)

        print(f"\tGenerated {ind}/{individuals} File:{filename} Points:{points:,}")
    print(f"\tFinished {problem.name}")
