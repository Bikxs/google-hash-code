import math
import random
import sys
import warnings

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
        self.cars = {}
        self.intersections = {}
        self.streets = {}
        self.lights = {}
        self.paths = {}


        self.reset()

    def step(self):

        print(f"timestep:{self.time_step}")

        def is_light_green(green_light_timing):

            for x in range(green_light_timing['start'], green_light_timing['end']):
                if self.time_step % x == 0:
                    return True
            return False

        for intersection_id in list(self.intersections):
            intersection = self.intersections[intersection_id]
            for street_name in list(intersection):
                street = intersection[street_name]
                green_light_timing = street['green_lights']
                street['served'] = False
                if is_light_green(green_light_timing):
                    street['light'] = 'GREEN'
                else:
                    street['light'] = 'RED'
        car_list =  list(self.cars)
        for car_id in car_list:
            car = self.cars[car_id]
            finished = car['finished']
            current_location_on_path = car['current_location_on_path']
            num_paths = car['num_paths']

            # check next item
            if (not finished) and self.time_step >= car['at_next_junction_time_step']:
                # check finished state
                if current_location_on_path == (len(car['path_streetnames']) - 1):
                    car['finished'] = True
                    car['finished_time'] = self.time_step
                    continue
                # check if car can use intersection
                next_junction = car['next_junction']

                intersection = self.intersections[next_junction]

                street_name = car['current_street_name']
                street = intersection[street_name]
                queue = street['queue']
                if car_id not in queue:
                    queue.append(car_id)
                if street['served'] == False:
                    if street['light'] == 'GREEN' and queue[0] == car_id:
                        # car can pass

                        current_location_on_path += 1
                        current_street_name = car['path_streetnames'][current_location_on_path]
                        next_intersection = self.streets[current_street_name].end
                        at_next_junction_time_step = self.streets[current_street_name].length + self.time_step

                        car['next_junction'] = next_intersection
                        car['at_next_junction_time_step'] = at_next_junction_time_step
                        car['current_street_name'] = current_street_name
                        car['current_location_on_path'] = current_location_on_path
                        queue.pop(0)
                    street['served'] == True
                    # update street intersection status
            finished = car['finished']
            print(f'\tcar{car_id}  loc:{current_location_on_path}/{num_paths-1} finished:{finished}')

        self.time_step += 1
    def reset(self, schedules=[]):
        self.time_step = 1
        self.streets = {street.street_name: street for street in self.problem.streets}
        self.cars = {}
        for path in self.problem.paths:
            next_intersection = self.streets[path.street_names[0]].end
            current_location_on_path = 0
            current_street_name = path.street_names[current_location_on_path]

            at_next_junction_time_step = self.streets[current_street_name].length

            self.cars[path.car_id] = {'next_junction': next_intersection,
                                      'at_next_junction_time_step': at_next_junction_time_step,
                                      'current_location_on_path': current_location_on_path,
                                      'current_street_name': current_street_name,
                                      'path_streetnames': path.street_names,
                                      'num_paths': len(path.street_names),
                                      'finished': False,
                                      'finished_time': self.duration}

        self.intersections = {}
        for intersection in self.problem.intersections:
            self.intersections[intersection.intersection_id] = {street: {
                'street': street, 'queue': [], 'light': 'RED', 'green_lights': [], 'schedule_time': 0} for
                street in
                intersection.incoming_street_names}
        for schedule in schedules:
            intersection = self.intersections[schedule.intersection_id]
            for street_name, street in intersection.items():
                street['green_lights'] = schedule.green_lights[street_name]

    def score(self):
        for time_step in range(self.duration):
            self.step()
        total_score = 0
        for car_id, car_status in self.cars.items():
            if car_status['finished']:
                total_score += (self.bonus_points_per_car + self.duration - car_status['finished_time'])

        return total_score


class Schedule:
    def __init__(self, intersection_id, number_of_incoming_streets_covered, green_lights):
        """
        ● the rst line containing a single integer i (0 ≤ i < I ) – the ID of the
        intersection,
        """
        self.intersection_id = intersection_id
        """
        ● the second line containing a single integer E i ( 0 < E i ) – the number of
        incoming streets (of the intersection i ) covered by this schedule,
        """
        self.number_of_incoming_streets_covered = number_of_incoming_streets_covered
        """
        ● Ei lines describing the order and duration of green lights. Each of those lines
        must contain (separated by a single space):
        ○ the street name,
        ○ an integer T ( 1 ≤ T ≤ D ) – for how long each street will have a green
        light.
        """
        self.green_lights = green_lights  # {(street_name:{start:0,end:0,duration:0}}


def strategy_round_robin():
    _schedules = []
    for intersection in problem.intersections:
        streets = intersection.incoming_street_names
        random.shuffle(streets)
        green_lights = {}
        time = 1
        for street in streets:
            duration = 1
            green_lights[street] = {'start': time,
                                    'end': time + duration,
                                    'duration': duration}
            time += duration

        schedule = Schedule(intersection_id=intersection.intersection_id,
                            number_of_incoming_streets_covered=len(green_lights),
                            green_lights=green_lights)
        _schedules.append(schedule)
    return _schedules


def strategy_by_number_of_cars():
    _schedules = []
    round_time = 10
    street_traffic = {street.street_name: 0 for street in problem.streets}
    for path in problem.paths:
        for streatname in path.street_names:
            street_traffic[streatname] += 1
    for intersection in problem.intersections:
        streets = intersection.incoming_street_names.copy()
        random.shuffle(streets)
        total_cars = sum([street_traffic[streetname] for streetname in streets])
        if total_cars > 0:
            def timing(streetname):
                return int(
                    math.ceil(
                        (street_traffic[streetname] / total_cars) * min(round_time, problem.simulation_duration)))

            green_lights = {}
            time = 1
            for street in streets:
                duration = timing(street)
                green_lights[street] = {'start': time,
                                        'end': time + duration,
                                        'duration': duration}
                time += duration

            schedule = Schedule(intersection_id=intersection.intersection_id,
                                number_of_incoming_streets_covered=len(green_lights),
                                green_lights=green_lights)
            _schedules.append(schedule)
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
        schedules = strategy_round_robin()
        # schedules = strategy_by_number_of_cars()
        sim.reset(schedules)
        points = sim.score()
        df_schedules = pd.DataFrame(
            [{'intersection_id': schedule.intersection_id,
              'number_of_incoming_streets_covered': schedule.number_of_incoming_streets_covered,
              'green_lights': schedule.green_lights
              } for
             schedule in schedules])

        df_schedules.sort_values(['intersection_id'], ascending=[True], inplace=True)
        df_schedules.set_index('intersection_id', inplace=True)
        print_df_head("Schedules", df_schedules, 20)

        filename, points, new_file = save_schedules_dataframe(problem.prefix, folder=folder_name, points=points,
                                                              df_schedules=df_schedules)
        if not new_file:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} Existing File Points:{points:,}")
        else:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} NEW FILE !!!! Points:{points:,}  *************")
    print(f"\tFinished {problem.name}")
