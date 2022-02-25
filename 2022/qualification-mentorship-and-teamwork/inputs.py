from typing import Dict, List

from utils import *


class Skill:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level

    def __repr__(self):
        return f'{self.name} L{self.level}'


class Contributor:
    def __init__(self, name: str, skills: List[Skill]):
        self.name = name
        self.skills = skills


    def __repr__(self):
        return f'{self.name}: {self.skills}'


class Project:
    def __init__(self, name: str,
                 duration: int,
                 score: int,
                 best_before: int,
                 roles: List[Skill]):
        self.name = name  # its name
        self.roles = roles
        self.duration = duration  # duration of the project in days (how long it takes to complete a project once it is started)
        self.score = score  # the score awarded for completing the project
        self.best_before = best_before  # if the project last day of work is strictly before the indicated day, it earns the full score. If it’s late (that is, the project is still worked on during or after its "best before day"), it gets one point less for each day it is late, but no less than zero points

    def __repr__(self):
        return f'{self.name} duration:{self.duration} score:{self.score} best_before:{self.best_before} roles:{self.roles}'
    def work_a_day(self):
        self.days_worked += 1
        if self.days_worked >= self.duration:
            self.completed = True

class Problem:
    contributor: Dict[str, Contributor]
    projects: Dict[str, Project]

    def __init__(self, filename: string):
        self.prefix = filename[0]
        self.filename = f"{INPUT_FOLDER}/{filename}"
        self.name = filename.replace(".txt", "")
        self.contributors = {}
        self.projects = {}

        with open(self.filename, 'r') as f:
            lines = [line.strip().split(' ') for line in f.readlines()]
        self.number_of_contributors = int(lines[0][0])  # number of contributors
        self.number_of_projects = int(lines[0][1])  # number of projects.

        # Contributor-Sections
        linenumber = 1
        for _ in range(self.number_of_contributors):
            contributor_name = lines[linenumber][0]
            contributor_skills_count = int(lines[linenumber][1])
            linenumber += 1
            contributor_skills = []
            for _ in range(contributor_skills_count):
                skill = Skill(lines[linenumber][0], int(lines[linenumber][1]))
                contributor_skills.append(skill)
                linenumber += 1
            contributor = Contributor(contributor_name, contributor_skills)
            self.contributors[contributor_name] = contributor
        # Project-Sections
        for _ in range(self.number_of_projects):
            project_name = lines[linenumber][0]  # name of the project
            days_to_complete = int(lines[linenumber][1])  # the number of days it takes to complete the project,
            score = int(lines[linenumber][2])  # the score awarded for project’s completion
            best_before = int(lines[linenumber][3])  # the “best before” day for the project,
            number_of_roles = int(lines[linenumber][4])  # the number of roles in the project.
            linenumber += 1
            roles = []
            for _ in range(number_of_roles):
                role = Skill(lines[linenumber][0], int(lines[linenumber][1]))
                roles.append(role)
                linenumber += 1
            project = Project(name=project_name,
                              duration=days_to_complete,
                              score=score,
                              best_before=best_before,
                              roles=roles)
            self.projects[project_name] = project

        self.available_time = max([project.best_before  + project.score for name,project in self.projects.items()])
    def __str__(self):
        return f'{self.name.upper()}\n\tnumber_of_contributors: {self.number_of_contributors}\n\tnumber_of_projects: {self.number_of_projects}'


def read_problem(filename) -> Problem:
    return Problem(filename)


if __name__ == '__main__':
    p = read_problem("a_an_example.in.txt")
    print(p)
    print("Contributors")
    for name, contributor in p.contributors.items():
        print(f"\t{contributor}")
    print("Projects")
    for name, project in p.projects.items():
        print(f"\t{project}")
