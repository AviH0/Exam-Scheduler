from typing import Tuple, List

import numpy as np

from state import State
from solver import *


class GeneticSolver(Solver):

    def __init__(self, loader: Dataloader, evaluator: Evaluator, initial_population=10):
        super(GeneticSolver, self).__init__(loader, evaluator)
        self.population = {State(course_list=loader.get_course_list(),
                                 date_list=loader.get_available_dates())
                           for _ in range(initial_population)}

    def solve(self, iterations=50):
        for _ in range(iterations):
            fitness = sorted([(state, self.evaluator(state)) for state in self.population],
                             key=lambda x: x[1], reverse=True)
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


    def _random_select(self, fitnesses: List[Tuple[State, float]]) -> State:
        random_index = np.random.geometric(0.5, len(fitnesses))
        return fitnesses[random_index][0]

    def _combine(self, x: State, y: State) -> State:
        new_dict = dict()
        for i, course in enumerate(x.courses_dict):
            if i < (len(x.courses_dict) / 2):
                new_dict[course] = x.courses_dict[course]
            else:
                new_dict[course] = y.courses_dict[course]
        return State(new_dict)

    def _mutate(self, s: State):
        if np.random.choice([True, False], p=[0.1, 0.9]):
            course = np.random.choice(s.courses_dict.keys())
            s.courses_dict[course][np.random.choice([0, 1])] += np.random.choice([-3, -2, -1, 1, 2, 3])
        return s
