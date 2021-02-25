import re

from utils import *


def output_solution(name, df_schedules: pd.DataFrame):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    df_schedules = df_schedules[df_schedules['value'] > 0]
    points = 0
    with open(output_filename, 'w') as the_file:
        """
            The rst line must contain a single integer A ( 0 ≤ A ≤ I ), the number of intersections
            for which you specify the schedule
        """
        the_file.write(f"{len(df_schedules)}\n")
        for row in range(len(df_schedules)):
            intersection_id =df_schedules['intersection_id'].iloc[row]
            number_of_incoming_streets_covered=df_schedules['number_of_incoming_streets_covered'].iloc[row]
            green_lights=df_schedules['green_lights'].iloc[row]
            """
            ● the rst line containing a single integer i (0 ≤ i < I ) – the ID of the
            intersection,
            """
            the_file.write(f'{intersection_id}\n')
            """
            ● the second line containing a single integer E i ( 0 < E i ) – the number of
            incoming streets (of the intersection i ) covered by this schedule,
            """
            the_file.write(f'{number_of_incoming_streets_covered}\n')
            """
            ● E i lines describing the order and duration of green lights. Each of those lines
            must contain (separated by a single space):
            ○ the street name,
            ○ an integer T ( 1 ≤ T ≤ D ) – for how long each street will have a green
            light.
            """


            team_size = df_schedules['team_size'].iloc[row]
            pizzas_list = ' '.join([str(x) for x in df_schedules['pizza_ids'].iloc[row]])
            points += df_schedules['value'].iloc[row]
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
