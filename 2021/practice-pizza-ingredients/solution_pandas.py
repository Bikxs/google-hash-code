import warnings
from itertools import chain

import pandas as pd

from code_utils import make_code_zip
from inputs import *

warnings.filterwarnings("ignore")

OUTPUT_FOLDER = 'output'


def output_solution(name: Text, df_deliveries: pd.DataFrame):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    df_deliveries = df_deliveries[df_deliveries['value'] > 0]
    points = 0
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(df_deliveries)}\n")
        for row in range(len(deliveries)):
            team_size = df_deliveries['team_size'].iloc[row]
            pizzas_list = df_deliveries['pizza_ids'].iloc[row]
            points += df_deliveries['value'].iloc[row]
            the_file.write(f'{team_size} {pizzas_list}\n')
    print(f'\tSolution saved: {output_filename}')
    return points


def print_df_head(title: string, df: pd.DataFrame, rows=5):
    print("----------------------------------------------------------------------------")
    print(title)
    print("----------------------------------------------------------------------------")
    print(df.head(rows))
    print()


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
        if not key in ['a', 'b', 'c', 'd', 'e']:
            continue
        problem = read_problem(problem_meta['filename'])

        print()
        print(problem)

        print("\tAnalysing....")

        # load data into pandas frame
        df_pizzas = pd.DataFrame(
            [{'pizza_id': pizza.id, 'num_ingredients': pizza.number_of_ingredients, 'ingredients': pizza.ingredients,
              'delivered': False} for
             pizza in problem.pizzas])
        df_pizzas.set_index('pizza_id', inplace=True)

        # sorting not need because of random sampling applied later
        # df_pizzas.sort_values(['num_ingredients'], ascending=[0], inplace=True)

        # print_df_head("Pizzas", df_pizzas, 20)

        df_teams = pd.DataFrame(
            [{'team_id': team.id, 'size': team.size, 'served': False} for
             team in problem.teams])
        df_teams.set_index('team_id', inplace=True)
        # print_df_head("Teams", df_teams, 20)

        # make deliveries
        deliveries = []
        delivery_id = 0
        remaining_pizzas = len(df_pizzas[df_pizzas['delivered'] == False])
        remaining_teams = len(
            df_teams.loc[(df_teams['served'] == False) & (df_teams['size'] <= remaining_pizzas), ['size']])
        skip_count = 0
        while remaining_teams > 0 and remaining_pizzas > 0:
            # pick random team
            df_team = df_teams[df_teams['served'] == False].sample(n=1, replace=False)
            team_id = df_team['size'].iloc[0]
            team_size = df_team['size'].iloc[0]
            if team_size > remaining_pizzas:
                if skip_count > 5:
                    # give up
                    break
                skip_count += 1
                continue
            skip_count = 0

            # pick random pizzas
            pool_size = min(remaining_pizzas, 100)

            df_pizzas_pool = df_pizzas[df_pizzas['delivered'] == False].sample(n=pool_size,
                                                                               replace=False)
            # first_pizza = df_pizzas_pool['pizza_id', 'ingredients'].iloc[0]
            # make difference table
            df_pizzas_selected = df_pizzas_pool.iloc[:team_size]
            ingredients = set(chain.from_iterable(
                [df_pizzas_selected['ingredients'].iloc[row] for row in range(len(df_pizzas_selected))]))
            selected_pizzas = df_pizzas_selected.index.values

            """ 
            For each delivery, the delivery score is the square of the total number of different ingredient_types of
            all the pizzas in the delivery
            """
            if len(selected_pizzas) == team_size:
                value = len(ingredients) ** 2
            else:
                value = 0
            # update master records
            delivery = {'delivery_id': delivery_id,
                        'team_id': team_id,
                        'team_size': team_size,
                        'pizza_ids': selected_pizzas,
                        'value': value}
            deliveries.append(delivery)

            df_teams.loc[df_teams.index.isin(df_team.index), 'served'] = True
            df_pizzas.loc[df_pizzas.index.isin(df_pizzas_selected.index), 'delivered'] = True

            remaining_pizzas = len(df_pizzas[df_pizzas['delivered'] == False])
            remaining_teams = len(
                df_teams.loc[(df_teams['served'] == False) & (df_teams['size'] <= remaining_pizzas), ['size']])

            delivery_id += 1

        df_deliveries = pd.DataFrame(deliveries)
        df_deliveries.set_index('delivery_id', inplace=True)

        # print("Finished Deliveries")
        # print_df_head("Pizzas", df_pizzas, 20)
        # print_df_head("Teams", df_teams, 20)
        # print_df_head("Deliveries", df_deliveries, 20)
        print("\tDone.")
        print()
        total_points = output_solution(problem.name, df_deliveries)
        print(f'\tTotal Points: {total_points:,}')
