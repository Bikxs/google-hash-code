from typing import Dict

from utils import *


class StreetInfo:
    def __init__(self, begin, end, street_name, length):
        self.begin = begin
        self.end = end
        self.street_name = street_name
        self.length = length

    def __str__(self):
        return f'{self.street_name} I{self.begin}-> I{self.end} {self.length} secs'


class PathInfo:
    def __init__(self, car_id, number_of_streets_traversed, street_names):
        self.car_id = car_id
        self.number_of_streets_traversed = number_of_streets_traversed
        self.street_names = street_names

    def __str__(self):
        return f'{self.car_id} Streets: {self.number_of_streets_traversed}'


class IntersectionInfo:
    def __init__(self, intersection_id, incoming_street_names, outgoing_street_names):
        self.intersection_id = intersection_id
        self.incoming_street_names = incoming_street_names
        self.outgoing_street_names = outgoing_street_names
        self.lights = {}

    def __str__(self):
        return f'{self.intersection_id} Incoming Streets: {self.incoming_street_names} Outgoing Streets: {self.outgoing_street_names}'


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


class Problem:
    streets:Dict[str, StreetInfo]
    paths: Dict[int, PathInfo]
    intersections: Dict[int, IntersectionInfo]
    def __init__(self, filename: string):
        self.prefix = filename[0]
        self.filename = f"{INPUT_FOLDER}/{filename}"
        self.name = filename.replace(".txt", "")
        self.streets = {}
        self.paths = {}

        car_id = 0
        i = 0
        with open(self.filename, 'r') as f:
            for line in f:
                line_data = line.strip().split(' ')
                if i == 0:
                    # an integer D ( 1 ≤ D ≤ 10 4 ) - the duration of the simulation, in seconds,
                    D = int(line_data[0])
                    self.simulation_duration = D
                    # an integer I ( 2 ≤ I ≤ 10 5 ) - the number of intersections (with IDs from 0 to I -1 ),
                    I = int(line_data[1])
                    self.number_of_intersections = I
                    # an integer S ( 2 ≤ S ≤ 10 5 ) - the number of streets,
                    S = int(line_data[2])
                    self.number_of_streets = S
                    # an integer V ( 1 ≤ V ≤ 10 3 ) - the number of cars,
                    V = int(line_data[3])
                    self.number_of_cars = V
                    # an integer F ( 1 ≤ F ≤ 10 3 ) - the bonus points for each car that reaches  its destination before time D .
                    F = int(line_data[4])
                    self.bonus_points_per_car = F
                elif 1 <= i < S + 1:

                    # The next S lines contain descriptions of streets. Each line contains:
                    # populate the streets

                    # two integers B and E ( 0 ≤ B < I , 0 ≤ E < I ) - the intersections at the start and the end of the street, respectively,
                    B = int(line_data[0])
                    E = int(line_data[1])
                    # the street name (a string consisting of between 3 and 30 lowercase ASCII characters a - z and the character - ),
                    street_name = line_data[2]
                    # an integer L ( 1 ≤ L ≤ D ) - the time it takes a car to get from the beginning to the end of that street.
                    L = int(line_data[3])
                    self.streets[street_name] = StreetInfo(begin=B, end=E, street_name=street_name, length=L)
                else:
                    # The next V lines describe the paths of each car. Each line contains:
                    # populate car paths
                    # an integer P ( 2 ≤ P ≤ 10 3 ) - the number of streets that the car wants to travel,
                    P = int(line_data[0])
                    """
                    followed by P names of the streets: The car sta s at the end of the  rst street (i.e. it waits for the green light to move to the next street)
                    and follows the schedule until the end of the last street. The schedule of a car is
                    always valid, i.e. the streets will be connected by intersections.
                    """
                    street_names = line_data[-P:]
                    self.paths[car_id] = PathInfo(car_id=car_id, number_of_streets_traversed=P,
                                                  street_names=street_names)
                    car_id += 1

                i += 1
        intersections_data = {}
        self.intersections = {}
        for street_name in self.streets:
            street = self.streets[street_name]
            if street.begin not in intersections_data:
                intersections_data[street.begin] = {'incoming': [], 'outgoing': []}
            if street.end not in intersections_data:
                intersections_data[street.end] = {'incoming': [], 'outgoing': []}

            intersections_data[street.end]['incoming'].append(street.street_name)
            intersections_data[street.begin]['outgoing'].append(street.street_name)
        for id, data in intersections_data.items():
            self.intersections[id] = IntersectionInfo(intersection_id=id,
                                                      incoming_street_names=list(set(data['incoming'])),
                                                      outgoing_street_names=list(set(data['outgoing'])))

    def __str__(self):
        return f'{self.name.upper()}\n\tFilename: {self.filename}\n\tSimulation Duration: {self.simulation_duration:,}\n\tStreets: {self.number_of_streets:,}\n\tIntersections: {self.number_of_intersections:,}\n\tCars: {self.number_of_cars:,}\n\tBonus Points: {self.bonus_points_per_car:,}'


def read_problem(filename) -> Problem:
    return Problem(filename)
