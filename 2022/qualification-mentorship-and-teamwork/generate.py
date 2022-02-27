import random
import sys
import warnings
from datetime import datetime

import simpy

from inputs import *
from utils import *

warnings.filterwarnings("ignore")


class Solution:
    def __init__(self, problem: Problem, assignments):
        self.problem = problem
        self.projects_days_worked = {name: 0 for name, project in problem.projects.items()}
        self.projects_status = {name: "waiting" for name, project in problem.projects.items()}
        self.contributor_assignment = {name: None for name, contributor in problem.contributors.items()}
        self.projects = problem.projects
        self.assignments = assignments  # project_name,[contributor_name]
        self.projects = problem.projects
        self.assignments = assignments

    @property
    def score(self):
        return sum([project.scored for _, project in self.projects.items()])

    def evaluate(self):
        env = simpy.Environment()
        contributors = []

        for project_name, assignment in self.assignments:
            # project_name = assignment[0]
            contributors.extend(assignment)
        contributors = list(set(contributors))
        contributor_resources = {contributor: simpy.Resource(env=env) for contributor in contributors}

        def project_process_gen(project: Project, contributors):

            # wait for the contributors
            resources = [contributor_resources[contributor] for contributor in contributors]
            requests = [resource.request() for resource in resources]
            # print(f"{env.now} Project {project.name} waiting for contributors {contributors}")
            for request in requests:
                yield request
            # print(f"{env.now} Project {project.name} started {contributors}")
            yield env.timeout(project.duration)
            # print(f"{env.now} Project {project.name} completed.",end=' ')
            # project.complete(env.now)
            for resource, request in zip(resources, requests):
                # release the resources
                resource.release(request)
            score = project.complete(env.now - 1)
            # print(f" Score: {score}")
            yield env.timeout(0)

        for project_name, contributors in self.assignments:
            project = self.projects[project_name]
            env.process(project_process_gen(project, contributors))
            # self.score += self.score
        env.run(until=problem.available_time + 10)
        return self.score


def gen_solution_a_text_book():
    return [("WebServer", ["Bob", "Anna"]),
            ("Logging", ["Anna"]),
            ("WebChat", ["Maria", "Bob"])]


def gen_random_assignments(problem):
    projects = [project for project_name, project in problem.projects.items()]
    random.shuffle(projects)
    contributors = [contributor for name, contributor in problem.contributors.items()]
    assignments = []
    for project in projects:
        assignment = []
        for (role_name, role_level) in project.roles:
            assigned = False
            avalailable_contributors = [contributor for contributor in contributors if
                                        contributor not in assignment and contributor.skills[role_name] >= role_level]
            random.shuffle(avalailable_contributors)
            for contributor in avalailable_contributors:
                skill_level = contributor.skills[role_name]
                if (skill_level >= role_level):
                    if contributor.name in assignment:
                        pass
                    else:
                        assignment.append(contributor.name)
                        if len(assignment) != len(set(assignment)):
                            print("A contributer has been assigned to same project twice")
                        assigned = True
                        break
            if assigned:
                continue
        if len(assignment) == len(project.roles):
            assignments.append((project.name, assignment))





    return assignments


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
    # print()
    # print(problem)
    # print("Contributors")
    # for name, contributor in problem.contributors.items():
    #     print(f"\t{contributor}")
    # print("Projects")
    # for name, project in problem.projects.items():
    #     print(f"\t{project}")

    # print("\tGenerating solution....")
    for _ in range(individuals):
        seed = datetime.now()
        random.seed(seed)

        # assignments = gen_solution_a_text_book()# gen_random_assignments(problem)
        assignments =  gen_random_assignments(problem)
        solution = Solution(problem, assignments=assignments)
        score = solution.evaluate()
        save_assignments_dict(problem.prefix, folder=folder_name, points=score, assignments=assignments)
        print(f"Score = {score}")
        break
    print(f"\tFinished {problem.name}")
