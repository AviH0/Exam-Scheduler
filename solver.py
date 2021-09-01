from abc import abstractmethod
from datetime import date
from typing import Iterable, Mapping, Callable

from dataloader import Dataloader
from objects import *
from state import Evaluator


class Solver:

    def __init__(self, loader: Dataloader, evaluator: Evaluator):
        """
        Create a solver for the problem data from loader with a specific evaluator.
        :param loader:
        :param evaluator:
        """
        self.course_list = loader.get_course_list()
        self.course_pair_evaluator = loader.get_course_pair_weights()
        self.moed_a_dates, self.moed_b_dates = loader.get_available_dates()
        self.evaluator = evaluator

    @abstractmethod
    def solve(self, progress_func: Callable):
        """
        Run solver to find solution.
        :return:
        """
        pass
