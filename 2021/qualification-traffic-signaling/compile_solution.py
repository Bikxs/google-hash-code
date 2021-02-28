import re

from utils import *


def output_solution(name, df_schedules: pd.DataFrame):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    points = 0
    with open(output_filename, 'w') as the_file:
        """
            The rst line must contain a single integer A ( 0 ≤ A ≤ I ), the number of intersections
            for which you specify the schedule
        """
        the_file.write(f"{len(df_schedules)}\n")
        for row in range(len(df_schedules)):
            intersection_id = df_schedules.index[row]

            green_lights = df_schedules['green_lights'].iloc[row]
            """
            ● the rst line containing a single integer i (0 ≤ i < I ) – the ID of the
            intersection,
            """
            the_file.write(f'{intersection_id}\n')


            green_lights_output = []

            for street_name, data in green_lights.items():
                if data['duration'] > 0:
                    green_lights_output.append((data['start'], data['end'], data['duration'], street_name))

            """
            ● the second line containing a single integer E i ( 0 < E i ) – the number of
            incoming streets (of the intersection i ) covered by this schedule,
            """
            number_of_incoming_streets_covered = len(green_lights_output)
            the_file.write(f'{number_of_incoming_streets_covered}\n')
            green_lights_output.sort()
            for start, end, duration, street_name in green_lights_output:
                """
                ● E i lines describing the order and duration of green lights. Each of those lines
                must contain (separated by a single space):
                ○ the street name,
                ○ an integer T ( 1 ≤ T ≤ D ) – for how long each street will have a green
                light.
                """
                the_file.write(f'{street_name} {duration}\n')
    return points


if __name__ == '__main__':
    make_code_zip(OUTPUT_FOLDER)
    folders_names = ['a_example', 'b_by_the_ocean', 'c_checkmate', 'd_daily_commute', 'e_etoile', 'f_forever_jammed']
    total_points = 0
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
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
            m = re.search('-(.+?).pickle', file)
            if m:
                points = int(m.group(1))
                solutions.append((points, file))
            else:
                continue
        solutions.sort(reverse=True)
        filename = f'{folder}/{solutions[0][1]}'
        points = solutions[0][0]
        df_best_solution = load_schedules(filename)

        output_solution(folder_name, df_best_solution)
        total_points += points
        points_str = f"{points:,}".rjust(15)
        print(f'{folder_name.upper().ljust(30)} Points: {points_str}\t{filename}')
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
    points_str = f"{total_points:,}".rjust(15)
    print("Total Points".ljust(38), points_str)
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
    print()
    print("You can now upload the code.zip and solutions files into the judge system")
    print("https://hashcodejudge.withgoogle.com/#/rounds/5879728443490304/submissions/")
    print("Good luck!!")

    print("\nBikxs")
