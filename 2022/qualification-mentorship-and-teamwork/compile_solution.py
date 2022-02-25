import random
import re

from utils import *


def output_solution(name, assignmets:Dict):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    points = 0
    with open(output_filename, 'w') as the_file:
        """
            The rst line must contain a single integer A ( 0 ≤ A ≤ I ), the number of intersections
            for which you specify the schedule
        """

        the_file.write(f"{len(assignmets)}\n")
        for assignmet in assignmets:
            project = assignmet[0]
            contributors = assignmet[1]
            the_file.write(f'{project}\n')
            for index,contributor in enumerate(contributors):
                the_file.write(f'{" " if index != 0 else ""}{contributor}')
            the_file.write("\n")

    return points


if __name__ == '__main__':
    make_code_zip(OUTPUT_FOLDER)
    folders_names = ['a_an_example.in', 'b_better_start_small.in', 'c_collaboration.in', 'd_dense_schedule.in', 'e_exceptional_skills.in', 'f_find_great_mentors.in']
    total_points = 0
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
    for folder_name in folders_names:
        folder = f'{INTERMEDIATE_FOLDER}/{folder_name}'
        if not os.path.exists(folder):
            continue
        files = os.listdir(folder)
        if not files:
            continue
        solutions = []
        for file in files:
            # extract the points
            m = re.search('-(.+?).json', file)
            if m:
                points = int(m.group(1))
                solutions.append((points, file))
            else:
                continue
        solutions.sort(reverse=True)
        solution = random.choice(solutions[:10])
        filename = f'{folder}/{solution[1]}'
        points = solution[0]
        df_best_solution = load_assignment(filename)

        output_solution(folder_name, df_best_solution)
        total_points += points
        solutions_str = f"{len(solutions):,}".rjust(4)
        points_str = f"{points:,}".rjust(10)
        print(f'{folder_name.upper().ljust(20)} Solutions: {solutions_str}\tPoints: {points_str}\t{filename}')
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
    points_str = f"{total_points:,}".rjust(19)
    print("Total Points".ljust(38), points_str)
    print(
        "--------------------------------------------------------------------------------------------------------------------------------------------------------")
    print()
    print("You can now upload the code.zip and solutions files into the judge system")
    # print("https://hashcodejudge.withgoogle.com/#/rounds/5879728443490304/submissions/")
    print("https://hashcodejudge.withgoogle.com/#/rounds/5977771406786560/submissions/")
    print("Good luck!!")

    print("\nBikxs")
