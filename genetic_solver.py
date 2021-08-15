from datetime import timedelta
from typing import Tuple, List, Set

import numpy as np

from state import State
from solver import *


class GeneticSolver(Solver):

    def __init__(self, loader: Dataloader, evaluator: Evaluator, initial_population=10):
        """
        Create a new genetic solver.
        :param loader: Dataloader for this problem.
        :param evaluator: Evaluator to use as fitness function for this problem.
        :param initial_population: Number of initial states to seed population at first generation.
        """
        super(GeneticSolver, self).__init__(loader, evaluator)
        self.population = {State(course_list=loader.get_course_list(),
                                 date_list=loader.get_available_dates())
                           for _ in range(initial_population)}

    def export_solution(self) -> Mapping[date, Iterable[Course]]:
        fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                         key=lambda x: x[1], reverse=True)
        solution_state: State = fitness[0][0]
        solution_mapping: Mapping[date, Set[Course]] = {d: set() for d in
                                                        self.moed_a_dates + self.moed_b_dates}
        for course in solution_state.courses_dict:
            solution_mapping[solution_state.courses_dict[course][0]].add(course)
            solution_mapping[solution_state.courses_dict[course][1]].add(course)
        return solution_mapping

    def solve(self, iterations=50):
        for _ in range(iterations):
            print(_)
            fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                             key=lambda x: x[1], reverse=False)
            new_population = set()
            for _ in range(len(self.population)):
                x = self._random_select(fitness)
                y = self._random_select(fitness)
                z = (self._combine(x, y))
                z = self._mutate(z)
                new_population.add(z)
            self.population = new_population
        fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                         key=lambda x: x[1], reverse=True)
        return fitness[0][0]

    @staticmethod
    def _random_select(fitnesses: List[Tuple[State, float]]) -> State:
        """
        Select a random subject from list of population with fitness values.
        :param fitnesses: List of tuples (state, fitness) where state is a state from population and fitness
         is the fitness evaluation for that state.
        :return: A randomly selected state where high fitness implies high probability of selection.
        """
        random_index = np.random.geometric(0.5) - 1
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
        if np.random.choice([True, False], p=[0.1, 0.9]):
            course = np.random.choice(list(s.courses_dict.keys()))
            days_to_move = [timedelta(days=-1), timedelta(days=-1), timedelta(days=0), timedelta(days=0),
                    timedelta(days=0), timedelta(days=1), timedelta(days=1)]
            moed = np.random.choice([0, 1])
            exam_dates = list(s.courses_dict[course])
            exam_dates[moed] += np.random.choice(days_to_move)
            s.courses_dict[course] = tuple(exam_dates)
        return s
