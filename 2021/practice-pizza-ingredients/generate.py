import sys
import warnings
from itertools import chain

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

            selected_pizzas = []
            selected_ingredients = []
            for x in range(team_size):
                all_ingedients = set(np.hstack(df_pizzas_pool['ingredients'].values)) - set(selected_ingredients)


                def calculate_diffence(ingredients):
                    # rem1 = all_ingedients - set(selected_ingredients)
                    return len(all_ingedients - set(ingredients))


                df_pizzas_pool['difference'] = df_pizzas_pool['ingredients'].apply(calculate_diffence)

                df_pizzas_pool_selected = df_pizzas_pool[df_pizzas_pool['difference'] == df_pizzas_pool['difference'].min()]
                df_pizzas_pool_selected.sort_values(by=['num_ingredients','pizza_id'], ascending=[True,True], inplace=True)
                selected_pizzas.append(df_pizzas_pool_selected.index.values[0])
                selected_ingredients.extend(df_pizzas_pool_selected['ingredients'].iloc[0])
                #print_df_head("Pizza Pool Selected", df_pizzas_pool_selected, 20)
                df_pizzas_pool = df_pizzas_pool[~df_pizzas_pool.index.isin(selected_pizzas)]
            # first_pizza = df_pizzas_pool['pizza_id', 'ingredients'].iloc[0]
            # make difference table
            df_pizzas_selected = df_pizzas_pool.iloc[:team_size]

            selected_pizzas.sort()
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

            df_teams.loc[df_teams.index.isin(df_team.index), 'served'] = True
            df_pizzas.loc[df_pizzas.index.isin(df_pizzas_selected.index), 'delivered'] = True

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
