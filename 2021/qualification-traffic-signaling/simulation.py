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


def log(message):
    return
    print(message)


class Car(sim.Component):
    streets: List[Street]
    path_info: PathInfo

    def __init__(self, env, bonus_point, sim_duration, path_info: PathInfo, streets: Dict[str, Street], *args,
                 **kwargs):
        self.env = env
        self.car_id = path_info.car_id
        sim.Component.__init__(self, name=f'Car#{self.car_id}', *args, **kwargs)
        self.path = path_info
        self.streets = [streets[street_name] for street_name in
                        path_info.street_names]
        self.finished = False
        self.finish_time = None
        self.bonus_point = bonus_point
        self.sim_duration = sim_duration
        self.score = 0

    def process(self):
        for index, street in enumerate(self.streets):
            if index == 0:
                log(
                    f'T{int(self.env.now())}: {self.name()} waiting at light "{street.light}" to go to "{self.streets[index + 1].street_name}"')
                if street.light is None:
                    breakpoint()
                if street.light.queue is None:
                    breakpoint()
                yield self.enter(street.light.queue)
                continue
            log(
                f'T{int(self.env.now())}: {self.name()} at start of "{street.street_name} Length:{street.length} units"')
            yield self.hold(street.length)
            log(f'T{int(self.env.now())}: {self.name()} at end of "{street.street_name}"')
            if index < (len(self.streets) - 1):
                log(f'T{int(self.env.now())}: {self.name()} waiting at light '
                    f'"{street.light}" to go to "{self.streets[index + 1].street_name}"')
                if street.light.color == GREEN:
                    self.enter(street.light.queue)
                    yield street.light.activate()
                else:

                    yield self.enter(street.light.queue)

                # self.leave(street.light.queue)

            # transition from street to street
        self.finished = True
        self.finish_time = self.env.now()
        self.score = self.bonus_point + self.sim_duration - self.finish_time
        log(f'T{int(self.env.now())}: {self.name()} score={self.score} Finished!!!!!!')

        self.passivate()

    def __str__(self):
        if self.finished:
            return f'{self.car_id}-{self.current_street_name} Finished!! @T{self.finished_time}'
        else:
            return f'{self.car_id}-{self.current_street_name}:{self.current_street_position}/{self.current_street_max_position}'


class Light(sim.Component):
    def __init__(self, street, intersection, *args, **kwargs):
        self.street = street
        self.intersection = intersection
        name = f'Light-I{intersection.intersection_id}:{self.street.street_name}'
        sim.Component.__init__(self, name=name, *args, **kwargs)
        self.color = RED
        self.queue = sim.Queue(name)

    def process(self):
        while True:
            if len(self.queue) == 0:
                yield self.passivate()
                continue
            assert len(self.queue) > 0
            car = self.queue.pop()
            car.activate()
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
        lights_list = [(light['start'], light['end'], light['duration'], street_name) for street_name, light in
                       self.schedule.green_lights.items()]
        lights_list.sort()
        if len(lights_list) == 1:
            light = self.lights[lights_list[0][3]]
            light.color = GREEN
            # log(f'T{self.env.now()}: {light.name()} turned "GREEN FOREVER"')
            light.activate()
            yield self.passivate()
            return
        while True:
            for start, end, duration, street_name in lights_list:
                light = self.lights[street_name]
                light.color = GREEN

                # log(f'T{self.env.now()}: {light.name()} turned "GREEN" queue = {len(light.queue)}')
                light.activate()
                yield self.hold(duration)
                light.passivate()
                light.color = RED

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
        env = sim.Environment(trace=False)
        log('Schedules:')
        for intersection_id, schedule in schedules.items():
            log(f'{intersection_id}:{schedule.green_lights}')
        log('')
        self.streets = {street_name: Street(street_info) for street_name, street_info in problem.streets.items()}
        self.intersections = {intersection_id: Intersection(intersection_info,
                                                            schedules[intersection_id],
                                                            self.streets)
                              for intersection_id, intersection_info in problem.intersections.items() if
                              intersection_id in schedules}
        self.cars = {car_id: Car(env, self.bonus_points_per_car, self.duration, path_info, streets=self.streets) for
                     car_id, path_info
                     in problem.paths.items()}
        env.run(duration=self.duration)
        log(f'T{int(env.now()) - 1}: Simulation Complete')

    @property
    def score(self):
        return sum(car.score for car_id, car in self.cars.items())
