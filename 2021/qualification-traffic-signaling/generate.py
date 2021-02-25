import math
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
        self.duration = problem.simulation_duration
        self.step = 0
        self.cars = {}
        self.intersections = {}
        self.reset()
        self.accumulated_score = 0

    def step(self):
        self.step = +1
        for car_id,car_status in self.cars.items():
            # check next item
            if self.step == car_status['at_next_junction_time_step']:
                # check if car can use intersection
                intersection_id = self.intersections[car_status['at_next_junction_time_step']]
                street = car_status['current_street_name']
                street_status = self.intersections[intersection_id][street]
                if street_status['light']== 'GREEN' and street_status['queue'][0]==car_id:
                    #car can pass
                    car_status['current_location_on_path'] += 1
                    current_street_name = car_status['path_streetnames'][car_status['current_location_on_path']]
                    next_intersection = self.streets[current_street_name].end
                    at_next_junction_time_step = self.streets[current_street_name].length

                    car_status['next_junction']= next_intersection
                    car_status['at_next_junction_time_step']= at_next_junction_time_step
                    car_status['current_street_name']= current_street_name

        # update street intersection status
        for intersection in self.problem.intersections:
            self.intersections[intersection.intersection_id] = {street: {'queue': [], 'light': 'RED'} for street in
                                                                intersection.incoming_street_names}



    def reset(self):
        self.step = 0
        self.streets = {street.street_name: street for street in self.problem.streets}
        self.cars = {}
        for path in self.problem.paths:
            next_intersection = self.streets[path.street_names[self.step]].end
            current_location_on_path = 0
            current_street_name = path.street_names[current_location_on_path]

            at_next_junction_time_step = self.streets[current_street_name].length

            self.cars[path.car_id] = {'next_junction': next_intersection,
                                      'at_next_junction_time_step': at_next_junction_time_step,
                                      'current_location_on_path':current_location_on_path,
                                      'current_street_name': current_street_name,
                                      'path_streetnames':path.street_names}

        self.intersections = {}
        for intersection in self.problem.intersections:
            self.intersections[intersection.intersection_id] = {street: {'queue': [], 'light': 'RED'} for street in
                                                                intersection.incoming_street_names}

    def score(self, schedules):
        return 0


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
        self.green_lights = green_lights


def strategy_round_robin():
    _schedules = []
    for intersection in problem.intersections:
        _schedules.append(
            Schedule(intersection_id=intersection.intersection_id,
                     number_of_incoming_streets_covered=len(intersection.incoming_street_names),
                     green_lights=[(street_name, 1) for street_name in intersection.incoming_street_names]))
    return _schedules


def strategy_by_number_of_cars():
    _schedules = []
    round_time = 10
    street_traffic = {street.street_name: 0 for street in problem.streets}
    for path in problem.paths:
        for streatname in path.street_names:
            street_traffic[streatname] += 1
    for intersection in problem.intersections:
        total_cars = sum([street_traffic[streetname] for streetname in intersection.incoming_street_names])
        if total_cars > 0:
            def timing(streetname):
                return int(
                    math.ceil(
                        (street_traffic[streetname] / total_cars) * min(round_time, problem.simulation_duration)))

            green_lights = [(street_name, timing(street_name)) for street_name in
                            intersection.incoming_street_names if timing(street_name) > 0]

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
        sim.reset()
        # schedules = strategy_round_robin()
        schedules = strategy_by_number_of_cars()
        points = sim.score(schedules)
        df_schedules = pd.DataFrame(
            [{'intersection_id': schedule.intersection_id,
              'number_of_incoming_streets_covered': schedule.number_of_incoming_streets_covered,
              'green_lights': schedule.green_lights
              } for
             schedule in schedules])

        df_schedules.sort_values(['intersection_id'], ascending=[True], inplace=True)
        df_schedules.set_index('intersection_id', inplace=True)
        print_df_head("Schedules", df_schedules[45:55], 20)

        filename, points, new_file = save_schedules_dataframe(problem.prefix, folder=folder_name, points=points,
                                                              df_schedules=df_schedules)
        if not new_file:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} Existing File Points:{points:,}")
        else:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} NEW FILE !!!! Points:{points:,}  *************")
    print(f"\tFinished {problem.name}")
