from typing import Tuple, List, Dict
import numpy as np
from state import State
from solver import *


class GeneticSolver(Solver):

    NUM_CALLS = 0
    def __init__(self, loader: Dataloader, evaluator: Evaluator,
                 initial_population=30, p_mutate=0.7, p_fittness_geom=0.3):
        """
        Create a new genetic solver.
        :param loader: Dataloader for this problem.
        :param evaluator: Evaluator to use as fitness function for this problem.
        :param initial_population: Number of initial states to seed population at first generation.
        :param p_mutate: Probability of a mutation during reproduction.
        :param p_fittness_geom: Probability of selection of a fit subject (Geometric)
        """
        super(GeneticSolver, self).__init__(loader, evaluator)
        self.population = [State(course_list=loader.get_course_list(),
                                 date_list=loader.get_available_dates())
                           for _ in range(initial_population)]
        self.__p_mutate = p_mutate
        self.__p_fitness_geom = p_fittness_geom

    def solve(self, progress_func: Callable, iterations=50, verbose=False):

        GeneticSolver.NUM_CALLS += 1

        for i in range(iterations):
            if verbose:
                print(i)

            self._update_prog_func(progress_func, i, iterations)

            fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                             key=lambda x: x[1], reverse=False)
            new_population = []
            for _ in range(len(self.population)):
                x = self._random_select(fitness)
                y = self._random_select(fitness)
                z = (self._combine(x, y))
                z = self._mutate(z)
                new_population.append(z)
            self.population = new_population
            if verbose:
                print(f"Current best fitness: {fitness[0][1]}")
        fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                         key=lambda x: x[1], reverse=False)
        return fitness[0][0]

    def _random_select(self, fitnesses: List[Tuple[State, float]]) -> State:
        """
        Select a random subject from list of population with fitness values.
        :param fitnesses: List of tuples (state, fitness) where state is a state from population and fitness
         is the fitness evaluation for that state.
        :return: A randomly selected state where high fitness implies high probability of selection.
        """
        random_index = np.random.geometric(self.__p_fitness_geom) - 1
        if random_index >= len(fitnesses):
            random_index = len(fitnesses) - 1
        return fitnesses[random_index][0]

    def _combine(self, x: State, y: State) -> State:
        """
        Combine two states to form a new state
        :param x: First state.
        :param y: Second State.
        :return: A new state where the first half of courses contains the dates from x and the second half
        contains the dates from y.
        """
        new_dict = dict()
        for i, course in enumerate(x.courses_dict):
            if i < (len(x.courses_dict) / 2):
                new_dict[course] = x.courses_dict[course]
            else:
                new_dict[course] = y.courses_dict[course]
        return State(new_dict)

    def _mutate(self, s: State):
        """
        With some low probability create a small random change in the solution.
        :param s: State to mutate.
        :return: s after mutation.
        """
        if np.random.choice([True, False], p=[self.__p_mutate, 1 - self.__p_mutate]):
            course = np.random.choice(list(s.courses_dict.keys()))
            exam_dates = list(s.courses_dict[course])

            moed_to_change = np.random.choice([0, 1])
            moed_to_keep_date = exam_dates[1 - moed_to_change]
            new_possible_dates = []

            for d in [self.moed_a_dates, self.moed_b_dates][moed_to_change]:
                if abs((d - moed_to_keep_date)).days >= MIN_DAYS_FROM_A_TO_B:
                    new_possible_dates.append(d)

            exam_dates[moed_to_change] = np.random.choice(new_possible_dates)
            s.courses_dict[course] = tuple(exam_dates)
        return s

    def _update_prog_func(self, progress_func, iter_i, num_iterations):
        progress = (iter_i / num_iterations) * 0.5
        if GeneticSolver.NUM_CALLS % 2 == 0:
            progress += 0.5
        progress_func(progress)
