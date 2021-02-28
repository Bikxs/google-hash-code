import math
import random
import sys
import warnings

from tqdm import tqdm

from inputs import *
from utils import *

warnings.filterwarnings("ignore")


def print_df_head(title: string, df: pd.DataFrame, rows=5):
    print("----------------------------------------------------------------------------")
    print(title)
    print("----------------------------------------------------------------------------")
    print(df.head(rows))
    print()


class Simulation(object):
    def __init__(self, problem):
        self.problem = problem
        self.bonus_points_per_car = problem.bonus_points_per_car
        self.duration = problem.simulation_duration
        self.time_step = 0
        self.cars = problem.cars
        self.intersections = problem.intersections
        self.verbose = False

    def step(self):

        self.time_step += 1
        if self.verbose:
            print(f'Time Step: T{self.time_step}')
            print('\tIntersetions')
        for intersection_id in self.intersections:
            intersection = self.intersections[intersection_id]
            intersection.step(self.time_step)
            if self.verbose:
                print(f'\t\tIntersection#{intersection_id} ')
            for light_name in intersection.lights:
                light = intersection.lights[light_name]
                if self.verbose:
                    print(f'\t\t\tLight on {light}')
        if self.verbose:
            print('\tCar')
        for car_id in self.cars:
            car = self.cars[car_id]
            car.step(self.time_step)
            if self.verbose:
                print(f'\t\tCar#{car}')

    def reset(self, schedules={}):
        self.time_step = 0
        for car_id in self.cars:
            self.cars[car_id].reset()
        if self.verbose:
            print(f'Streets')
            for street_name, street in self.problem.streets.items():
                print(f'\t{street}')
            print(f'Intersections')
        for intersection_id in self.intersections:
            intersetion_schedule = schedules[intersection_id] if intersection_id in schedules else None
            self.intersections[intersection_id].reset(intersetion_schedule)
            if self.verbose:
                if intersetion_schedule is not None:
                    print(
                        f'\tintersection#{intersection_id} {intersetion_schedule.green_lights} Total Duration:{intersetion_schedule.total_round_time}')

    def score(self):
        for time_step in tqdm(range(self.duration)):
            self.step()
        total_score = 0
        for car_id, car in self.cars.items():
            if car.finished:
                total_score += (self.bonus_points_per_car + self.duration - car.finished_time)

        return total_score


class Schedule:
    def __init__(self, intersection_id, green_lights):
        """
        ● the rst line containing a single integer i (0 ≤ i < I ) – the ID of the
        intersection,
        """
        self.intersection_id = intersection_id
        """
        ● the second line containing a single integer E i ( 0 < E i ) – the number of
        incoming streets (of the intersection i ) covered by this schedule,
        """

        """
        ● Ei lines describing the order and duration of green lights. Each of those lines
        must contain (separated by a single space):
        ○ the street name,
        ○ an integer T ( 1 ≤ T ≤ D ) – for how long each street will have a green
        light.
        """
        self.green_lights = green_lights  # {(street_name:{start:0,end:0,duration:0}}
        self.total_round_time = sum(
            [light_schedule['duration'] for street_name, light_schedule in self.green_lights.items()])


def strategy_round_robin():
    _schedules = {}
    for intersection_id in problem.intersections:
        intersection = problem.intersections[intersection_id]
        streets = intersection.incoming_streets
        random.shuffle(streets)
        green_lights = {}
        time = 1
        for street in streets:
            duration = 1 + random.randint(0, 1)
            green_lights[street.street_name] = {'start': time,
                                                'end': time + duration,
                                                'duration': duration}
            time += duration

        schedule = Schedule(intersection_id=intersection.intersection_id,
                            green_lights=green_lights)
        _schedules[intersection_id] = schedule
    return _schedules


def strategy_by_number_of_cars():
    _schedules = {}

    street_traffic = {street_name: 0 for street_name, street in problem.streets.items()}
    for _, path in problem.paths.items():
        for streat_name in path.street_names:
            street_traffic[streat_name] += 1
    for intersection_id in problem.intersections:
        intersection = problem.intersections[intersection_id]
        streets = intersection.incoming_streets.copy()
        round_time = min(random.randint(len(streets), math.ceil(len(streets) * 2.5)), problem.simulation_duration)
        random.shuffle(streets)
        total_cars = sum([street_traffic[street.street_name] for street in streets])
        if total_cars > 0:
            def timing(streetname):
                return int(
                    math.ceil(
                        (street_traffic[streetname] / total_cars) * round_time))

            green_lights = {}
            time = 0
            for street in streets:
                duration = timing(street.street_name)
                green_lights[street.street_name] = {'start': time,
                                                    'end': time + duration,
                                                    'duration': duration}
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
    sim = Simulation(problem)
    for ind in range(individuals):
        if random.random() < 0.3:
            schedules = strategy_round_robin()
        else:
            schedules = strategy_by_number_of_cars()
        sim.reset(schedules)
        points = sim.score()
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
