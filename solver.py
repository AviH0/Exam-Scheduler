from abc import abstractmethod
from datetime import date
from typing import Dict, Iterable, Mapping

from dataloader import Dataloader
from objects import Course
from state import Evaluator


class Solver:


    def __init__(self, loader:Dataloader, evaluator:Evaluator):
        """
        Create a solver for the problem data from loader with a specific evaluator.
        :param loader:
        :param evaluator:
        """
        self.course_list = loader.get_course_list()
        self.course_pair_evaluator = loader.get_course_pair_weights()
        self.moed_a_dates, self.moed_b_dates = loader.get_available_dates()

    @abstractmethod
    def solve(self):
        """
        Run solver to find solution.
        :return:
        """
        pass

    @abstractmethod
    def export_solution(self) -> Mapping[date, Iterable[Course]]:
        """
        Return an schedule for exams as a  mapping from date to iterable of courses.
        :return:
        """
        pass
