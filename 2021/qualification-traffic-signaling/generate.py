import math
import random
import sys
import warnings
from datetime import datetime

from inputs import *
from simulation import Simulation
from utils import *

warnings.filterwarnings("ignore")


def print_df_head(title: string, df: pd.DataFrame, rows=5):
    print("----------------------------------------------------------------------------")
    print(title)
    print("----------------------------------------------------------------------------")
    print(df.head(rows))
    print()


def strategy_round_robin() -> Dict[int, Schedule]:
    _schedules = {}

    street_traffic = {street_name: 0 for street_name, street in problem.streets.items()}
    for _, path in problem.paths.items():
        for streat_name in path.street_names:
            street_traffic[streat_name] += 1
    for intersection_id in problem.intersections:
        intersection = problem.intersections[intersection_id]
        streets = intersection.incoming_street_names.copy()

        random.shuffle(streets)
        # streets.sort(reverse=True)
        total_cars = sum([street_traffic[street] for street in streets])
        if total_cars > 0:
            def timing(streetname):
                if street_traffic[streetname] == 0:
                    return 0
                return 1  # + random.randint(0, 2)  # round_time / len(streets)

                # return int(
                #     math.ceil(
                #         (street_traffic[streetname] / total_cars) * round_time))

            green_lights = {}
            time = 0
            for street in streets:
                duration = timing(street)
                green_lights[street] = {'start': time,
                                        'end': time + duration,
                                        'duration': duration}
                time += duration

            schedule = Schedule(intersection_id=intersection.intersection_id,
                                green_lights=green_lights)
            _schedules[intersection_id] = schedule
    return _schedules


def strategy_example_a() -> Dict[int, Schedule]:
    _schedules = {
        1: Schedule(1, green_lights={'rue-d-athenes': {'start': 0, 'end': 2, 'duration': 2},
                                     'rue-d-amsterdam': {'start': 2, 'end': 3,
                                                         'duration': 1}}),
        0: Schedule(0, green_lights={'rue-de-londres': {'start': 0, 'end': 2, 'duration': 2}}),
        2: Schedule(2, green_lights={'rue-de-moscou': {'start': 0, 'end': 1, 'duration': 1}}),
    }
    return _schedules


def strategy_by_number_of_cars() -> Dict[int, Schedule]:
    _schedules = {}

    street_traffic = {street_name: 0 for street_name, street in problem.streets.items()}
    for _, path in problem.paths.items():
        for streat_name in path.street_names:
            street_traffic[streat_name] += 1
    for intersection_id in problem.intersections:
        intersection = problem.intersections[intersection_id]
        streets = intersection.incoming_street_names.copy()
        round_time = min(random.randint(len(streets) * 2, math.ceil(len(streets) * 4)), 10, problem.simulation_duration)
        random.shuffle(streets)
        total_cars = sum([street_traffic[street] for street in streets])
        if total_cars > 0:
            def timing(streetname):
                return int(
                    math.ceil(
                        (street_traffic[streetname] / total_cars) * round_time))

            green_lights = {}
            time = 0
            for street in streets:
                duration = timing(street)
                green_lights[street] = {'start': time,
                                        'end': time + duration,
                                        'duration': duration}
                # if duration > 0:
                #     duration += random.randint(-duration, int(round_time / 2))
                time += duration

            schedule = Schedule(intersection_id=intersection.intersection_id,
                                green_lights=green_lights)
            _schedules[intersection_id] = schedule
    return _schedules


def strategy_by_number_of_cars_ignore_long_trips() -> Dict[int, Schedule]:
    _schedules = {}

    street_traffic = {street_name: 0 for street_name, street in problem.streets.items()}
    for car_id in problem.paths:
        path = problem.paths[car_id]
        path.length = sum([problem.streets[street_name].length for street_name in path.street_names])
    paths_list = [(path.length, random.random(), path) for car_id, path in problem.paths.items()]
    paths_list.sort()
    # paths = {path.car_id:path for _,path in paths_list}
    for _, _, path in paths_list[:int(math.ceil(len(paths_list) * .8))]:
        for streat_name in path.street_names:
            street_traffic[streat_name] += 1
    for intersection_id in problem.intersections:
        intersection = problem.intersections[intersection_id]
        streets = intersection.incoming_street_names.copy()
        round_time = min(random.randint(len(streets) * 4, math.ceil(len(streets) * 8)), 10, problem.simulation_duration)
        random.shuffle(streets)
        total_cars = sum([street_traffic[street] for street in streets])
        if total_cars > 0:
            def timing(streetname):
                return int(
                    math.ceil(
                        (street_traffic[streetname] / total_cars) * round_time))

            green_lights = {}
            time = 0
            for street in streets:
                duration = timing(street)
                if duration == 0:
                    duration = 1
                green_lights[street] = {'start': time,
                                        'end': time + duration,
                                        'duration': duration}
                # if duration > 0:
                #     duration += random.randint(-duration, int(round_time / 2))
                time += duration

            schedule = Schedule(intersection_id=intersection.intersection_id,
                                green_lights=green_lights)

            _schedules[intersection_id] = schedule
    return _schedules


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

    # for intersections in problem.intersections:
    #     print(intersections)

    print("\tGenerating schedules....")
    print()

    for ind in range(individuals):
        # schedules = strategy_round_robin()

        seed = datetime.now()
        random.seed(seed)
        # current date and time

        # schedules = strategy_round_robin()
        # schedules = strategy_by_number_of_cars()
        schedules = strategy_by_number_of_cars_ignore_long_trips()
        # schedules = strategy_example_a()
        points = Simulation(problem, schedules).score
        df_schedules = pd.DataFrame(
            [{'intersection_id': schedule.intersection_id,
              'green_lights': schedule.green_lights
              } for
             intersection_id, schedule in schedules.items()])

        df_schedules.sort_values(['intersection_id'], ascending=[True], inplace=True)
        df_schedules.set_index('intersection_id', inplace=True)
        # print_df_head("Schedules", df_schedules, 20)

        filename, points, new_file = save_schedules_dataframe(problem.prefix, folder=folder_name, points=points,
                                                              df_schedules=df_schedules)
        if not new_file:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} Existing File Points:{points:,}")
        else:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} NEW FILE !!!! Points:{points:,}  *************")
    print(f"\tFinished {problem.name}")
