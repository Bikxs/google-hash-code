import random
import sys
import warnings
from datetime import datetime

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

    def score(self):
        score = 0
        final_assignments = []
        for day in range(self.problem.available_time):
            for project_name, assignments in self.assignments:
                # project = self.projects[project_name]
                if self.projects_status[project_name] == "completed":
                    continue
                if self.projects_status[project_name] == "started":
                    self.projects_days_worked[project_name] = self.projects_days_worked[project_name] + 1
                    if self.projects_days_worked[project_name] >= self.projects[project_name].duration:
                        self.projects_status[project_name] = "completed"
                    if self.projects_status[project_name] == "completed":
                        # release the workers
                        for worker_name in assignments:
                            self.contributor_assignment[worker_name] = None
                        # take the score
                        best_before = self.projects[project_name].best_before
                        project_score = self.projects[project_name].score
                        if best_before >= day:
                            scored = project_score

                        else:
                            days_late = (day + 1) - best_before
                            scored = project_score - days_late
                            if scored < 0:
                                scored = 0
                        if scored > 0:
                            final_assignments.append((project_name,assignments))
                            score += scored
                else:
                    # try to start the project
                    read_to_start = True
                    for worker_name in assignments:
                        if self.contributor_assignment[worker_name] == None:
                            self.contributor_assignment[worker_name] = project_name
                        elif self.contributor_assignment[worker_name] == project_name:
                            continue
                        else:
                            # worker assigned to another project
                            read_to_start = False
                    if read_to_start:
                        self.projects_status[project_name] = "started"
                        if day == 0:
                            self.projects_days_worked[project_name] = self.projects_days_worked[project_name] + 1
        return score,final_assignments


def gen_solution_assinment():
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
        for role in project.roles:
            assigned = False
            avalailable_contributors = [contributor for contributor in contributors if contributor not in assignment]
            random.shuffle(avalailable_contributors)
            for contributor in avalailable_contributors:
                for skill in contributor.skills:
                    if skill.name == role.name and skill.level >= role.level:
                        assignment.append(contributor.name)
                        assigned = True
                        continue
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

        assignments = gen_random_assignments(problem)
        solution = Solution(problem, assignments=assignments)
        score,final_assignments = solution.score()
        save_assignments_dict(problem.prefix, folder=folder_name, points=score, assignments=final_assignments)
        # print(f"Score = {solution.score()}")
    print(f"\tFinished {problem.name}")
