import pandas as pd

from process import Text

OUTPUT_FOLDER = 'output'


def output_solution(name: Text, df_deliveries: pd.DataFrame):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    df_deliveries = df_deliveries[df_deliveries['value'] > 0]
    points = 0
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(df_deliveries)}\n")
        for row in range(len(df_deliveries)):
            team_size = df_deliveries['team_size'].iloc[row]
            pizzas_list = df_deliveries['pizza_ids'].iloc[row]
            points += df_deliveries['value'].iloc[row]
            the_file.write(f'{team_size} {pizzas_list}\n')
    print(f'\tSolution saved: {output_filename}')
    return points


if __name__ == '__main__':
    make_code_zip(OUTPUT_FOLDER)
