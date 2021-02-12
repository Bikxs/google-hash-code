import re

from utils import *


def output_solution(name, df_deliveries: pd.DataFrame):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    df_deliveries = df_deliveries[df_deliveries['value'] > 0]
    points = 0
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(df_deliveries)}\n")
        for row in range(len(df_deliveries)):
            team_size = df_deliveries['team_size'].iloc[row]
            pizzas_list = ' '.join([str(x) for x in df_deliveries['pizza_ids'].iloc[row]])
            points += df_deliveries['value'].iloc[row]
            the_file.write(f'{team_size} {pizzas_list}\n')
    return points


if __name__ == '__main__':
    make_code_zip(OUTPUT_FOLDER)
    folders_names = ['a_example', 'b_little_bit_of_everything', 'c_many_ingredients', 'd_many_pizzas', 'e_many_teams']
    total_points = 0
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    for folder_name in folders_names:
        folder = f'{INTERMEDIATE_FOLDER}/{folder_name}'
        if not os.path.exists(folder):
            break
        files = os.listdir(folder)
        if not files:
            break
        solutions = []
        for file in files:
            # extract the points
            m = re.search('-(.+?).csv', file)
            if m:
                points = int(m.group(1))
                solutions.append((points, file))
            else:
                continue
        solutions.sort(reverse=True)
        filename = f'{folder}/{solutions[0][1]}'
        best_solution_points, df_best_solution = load_deliveries(filename)

        points = output_solution(folder_name, df_best_solution)
        total_points += points
        points_str = f"{points:,}".rjust(15)
        print(f'{folder_name.upper().ljust(30)} Points: {points_str}\t{filename}')
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    points_str = f"{total_points:,}".rjust(15)
    print("Total Points".ljust(38), points_str)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    print()
    print("You can now upload the code.zip and solutions files into the judge system")
    print("https://hashcodejudge.withgoogle.com/#/rounds/5751229732880384/submissions/")
    print("Good luck!!")

    print("\nBikxs")
