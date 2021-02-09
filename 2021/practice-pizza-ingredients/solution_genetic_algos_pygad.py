from random import sample

import pandas as pd

import pygad_fork as pygad
from code_utils import make_code_zip
from inputs import *

OUTPUT_FOLDER = 'output'
POPULATION_SIZE = 20
NUM_GENERATIONS = 100  # Number of generations.
NUM_PARENTS_MATING = 10  # Number of solutions to be best_ind as parents in the mating pool.
PARENT_SELECTION_TYPE = "tournament"  # Type of parent selection.
K_TOURNAMENT = 7
PARENTS_TO_KEEP = 7  # Number of parents to keep in the next population. -1 means keep all parents and 0 means keep nothing.
CROSSOVER_TYPE = "cycle"  # Type of the crossover operator.
# Parameters of the mutation operation.
MUTATION_TYPE = "swap2"  # Type of the mutation operator.
MUTATION_PERCENT_GENES = 20.0  # Percentage of genes to mutate. This parameter has no action if the parameter mutation_num_genes exists or when MUTATION_TYPE is None.


class Delivery:
    def __init__(self, team_size: int, pizzas: List[Pizza]):
        self.team_size = team_size
        self.pizzas = [pizza for pizza in pizzas if pizzas != -1]
        if len(pizzas) != team_size:
            self.value = 0
        else:
            ingredients = []
            for pizza in pizzas:
                ingredients.extend(pizza.ingredients)
            self.value = len(set(ingredients)) ** 2
            """For each delivery, the delivery score is the square of the total number of different ingredients of
            all the pizzas in the delivery
            """

    def __str__(self):
        pizzas_list = ' '.join([str(pizza.index) for pizza in self.pizzas])
        return f'{self.team_size} {pizzas_list}'


Genome = List[int]


def generate_genome(problem: Problem, num_genes) -> Genome:
    all_pizzas = [x for x in range(problem.pizza_count)]
    return sample(all_pizzas, num_genes)


def output_solution(name: Text, solution: Genome):
    output_filename = f"{OUTPUT_FOLDER}/{name}.out"
    with open(output_filename, 'w') as the_file:
        the_file.write(f"{len(solution.deliveries)}\n")
        for _delivery in solution.deliveries:
            the_file.write(f"{_delivery}\n")
    print(f'Solution saved {output_filename}')


if __name__ == '__main__':
    probs = problems()
    make_code_zip(OUTPUT_FOLDER)
    print()
    print(f"Population size: {POPULATION_SIZE}")
    for problem in probs:
        print(problem.filename)
        print(problem)
        num_genes = min(problem.people_count, problem.pizza_count)
        genomes = [generate_genome(problem, num_genes) for x in range(POPULATION_SIZE)]


        def fitness_function(solution, solution_idx):
            people = problem.people[:num_genes]
            teams = problem.teams[:num_genes]

            data = pd.DataFrame(data={'people': people, 'teams': teams,
                                      'pizzas': solution}).set_index(
                'people')
            group = data.groupby(['teams']).agg(list)
            deliveries = []
            for team_number, row in group.iterrows():
                team_size = problem.team_sizes[team_number]
                team_pizzas = [problem.pizzas[int(pizza_number)] for pizza_number in row['pizzas'] if
                               pizza_number != -1]
                deliveries.append(Delivery(team_size, team_pizzas))

            return sum(delivery.value for delivery in deliveries)


        last_fitness = 0


        def callback_generation(ga_instance):
            global last_fitness
            print("Generation: {generation}".format(generation=ga_instance.generations_completed))
            print("\tFitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
            print("\tChange     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
            last_fitness = ga_instance.best_solution()[1]


        # Creating an instance of the GA class inside the ga module. Some parameters are initialized within the constructor.
        ga_instance = pygad.GA(num_generations=NUM_GENERATIONS,
                               num_parents_mating=NUM_PARENTS_MATING,
                               fitness_func=fitness_function,
                               initial_population=genomes,
                               parent_selection_type=PARENT_SELECTION_TYPE,
                               K_tournament=K_TOURNAMENT,
                               keep_parents=PARENTS_TO_KEEP,
                               crossover_type=CROSSOVER_TYPE,
                               mutation_type=MUTATION_TYPE,
                               mutation_percent_genes=MUTATION_PERCENT_GENES,
                               mutation_by_replacement=True,
                               on_generation=callback_generation,
                               gene_space=[x for x in range(problem.pizza_count)])

        # Running the GA to optimize the parameters of the function.
        ga_instance.run()

        # After the generations complete, some plots are showed that summarize the how the outputs/fitenss values evolve over generations.
        ga_instance.plot_result(title=f"{problem.name}\nIteration vs Fitness")

        # Returning the details of the best individual.
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        print(f"Parameters of the best solution : {solution}")
        print(f"Fitness value of the best solution = {solution_fitness}")
        print(f"Index of the best solution : {solution_idx}")

        if ga_instance.best_solution_generation != -1:
            print(f"Best fitness value reached after {ga_instance.best_solution_generation} generations.")
