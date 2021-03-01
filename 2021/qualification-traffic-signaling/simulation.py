from typing import List

import salabim as sim

from inputs import *

GREEN = 'GREEN'
RED = 'RED'


class Street:
    def __init__(self, street_info: StreetInfo):
        self.begin = street_info.begin
        self.end = street_info.end
        self.street_name = street_info.street_name
        self.length = street_info.length
        self.light = None
        self.cars = {}

    def __str__(self):
        return f'{self.street_name} I{self.begin}-> I{self.end} {self.length} secs'


class Car(sim.Component):
    streets: List[Street]
    path_info: PathInfo

    def __init__(self, path_info: PathInfo, streets: Dict[str, Street], *args, **kwargs):
        self.car_id = path_info.car_id
        sim.Component.__init__(self, name=f'Car#{self.car_id}', *args, **kwargs)
        self.path = path_info
        self.streets = [streets[street_name] for street_name in
                        path_info.street_names]
        self.finished = False
        self.finish_time = None

    def process(self):
        for street in self.streets:
            yield self.hold(street.lenth)
            self.enter(street.light.queue)
            # transition from street to street

    def __str__(self):
        if self.finished:
            return f'{self.car_id}-{self.current_street_name} Finished!! @T{self.finished_time}'
        else:
            return f'{self.car_id}-{self.current_street_name}:{self.current_street_position}/{self.current_street_max_position}'


class Light(sim.Component):
    def __init__(self, street, intersection, *args, **kwargs):
        self.street = street
        self.intersection = intersection
        self.name = f'Light-{self.street.street_name}_{self.intersection.intersection_id}'
        sim.Component.__init__(self, name=self.name, *args,
                               **kwargs)
        self.color = RED
        self.queue = sim.Queue('queue')

    def process(self):
        while True:
            yield self.hold(1)

    def __str__(self):
        return f'{self.intersection.intersection_id}-{self.street.street_name}: {self.color}'


class Intersection(sim.Component):
    intersection_id: int
    lights: Dict[int, Light]
    schedule: Schedule
    incoming_streets: Dict[str, Street]
    outgoing_streets: Dict[str, Street]

    def __init__(self, intersection_info: IntersectionInfo, schedule, streets: Dict[str, Street], *args, **kwargs):
        self.intersection_id = intersection_info.intersection_id
        sim.Component.__init__(self, name=f'Intersection{self.intersection_id}', *args, **kwargs)
        self.incoming_streets = {street_name: streets[street_name] for street_name in
                                 intersection_info.incoming_street_names}
        self.outgoing_streets = {street_name: streets[street_name] for street_name in
                                 intersection_info.outgoing_street_names}
        self.schedule = schedule
        self.lights = {}
        for street_name in self.incoming_streets:
            street = self.incoming_streets[street_name]
            light = Light(street, self)
            street.light = light
            self.lights[street.street_name] = light

    def process(self):
        while True:
            yield self.hold(1)

    def __str__(self):
        return f'{self.intersection_id} Incoming Streets: {self.incoming_streets} Outgoing Streets: {self.outgoing_streets}'


class Simulation(object):
    streets: Dict[str, Street]
    intersections: Dict[str, Intersection]
    cars: Dict[str, Car]

    def __init__(self, problem: Problem, schedules: Dict[int, Schedule]):
        self.problem = problem
        self.bonus_points_per_car = problem.bonus_points_per_car
        self.duration = problem.simulation_duration
        self.time_step = 0
        env = sim.Environment(trace=True)
        self.streets = {street_name: Street(street_info) for street_name, street_info in problem.streets.items()}
        self.intersections = {intersection_id: Intersection(intersection_info,
                                                            schedules[intersection_id],
                                                            self.streets)
                              for intersection_id, intersection_info in problem.intersections.items()}
        self.cars = {car_id: Car(path_info, streets=self.streets) for car_id, path_info in problem.paths.items()}
        env.run(till=self.duration)

    @property
    def score(self):
        total_score = 0
        for car_id, car in self.cars.items():
            if car.finished:
                total_score += (self.bonus_points_per_car + self.duration - car.finish_time)
        return total_score
