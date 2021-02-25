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
        # load data into pandas frame
        df_streets = pd.DataFrame(
            [{'begin': street.begin, 'end': street.end, 'street_name': street.street_name,
              'length': street.length
              } for
             street in problem.streets])
        df_streets.set_index('street_name', inplace=True)
        print_df_head("Streets", df_streets, 20)

        df_intersections = pd.DataFrame(
            [{'intersection_id': intersection.intersection_id, 'incoming_street_names': intersection.incoming_street_names,
              'outgoing_street_names': intersection.outgoing_street_names
              } for
             intersection in problem.intersections])
        df_intersections.set_index('intersection_id', inplace=True)
        print_df_head("Intersections", df_intersections, 20)

        df_paths = pd.DataFrame(
            [{'car_id': path.car_id, 'number_of_streets_traversed': path.number_of_streets_traversed,
              'street_names': path.street_names
              } for
             path in problem.paths])
        df_paths.set_index('car_id', inplace=True)
        print_df_head("Paths", df_paths, 20)

        # round robin green lights of 1 sec
        schedules = []
        for intersection in problem.intersections:
            schedules.append(
                Schedule(intersection_id=intersection.intersection_id,
                         number_of_incoming_streets_covered=len(intersection.incoming_street_names),
                         green_lights=[(street_name, 1) for street_name in intersection.incoming_street_names]))

        df_schedules = pd.DataFrame(
            [{'intersection_id': schedule.intersection_id, 'number_of_incoming_streets_covered': schedule.number_of_incoming_streets_covered,
              'green_lights': schedule.green_lights
              } for
             schedule in schedules])
        df_schedules.set_index('intersection_id', inplace=True)
        print_df_head("Schedules", df_schedules, 20)

        filename, points, new_file = save_schedules_dataframe(problem.prefix, folder=folder_name,
                                                              df_schedules=df_schedules)
        if not new_file:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} Existing File Points:{points:,}")
        else:
            print(f"\t{problem.name.upper()}: {ind}/{individuals} NEW FILE !!!! Points:{points:,}  *************")
    print(f"\tFinished {problem.name}")

if __name__ == '__main__':
    pass
