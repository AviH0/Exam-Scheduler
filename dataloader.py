from abc import abstractmethod
from typing import List, Callable, Tuple
from datetime import date
from datetime import timedelta
from objects import Course


class Dataloader:

    def __init__(self, startA: date, startB: date, end: date, not_allowed: List[date]):
        self.startA = startA
        self.startB = startB
        self.end = end
        self.not_allowed = not_allowed
        self.moedA_dates = []
        self.moedB_dates = []


    def _create_available_dates(self):
        one_day = timedelta(days=1)
        cur_date = self.startA
        while cur_date != self.startB:
            if cur_date.isoweekday() != 6 and cur_date not in self.not_allowed:
                self.moedA_dates.append(cur_date)
            cur_date += one_day

        while cur_date != self.end:
            if cur_date.isoweekday() != 6 and cur_date not in self.not_allowed:
                self.moedB_dates.append(cur_date)
            cur_date += one_day

    @abstractmethod
    def get_course_list(self) -> List[Course]:
        """
        Return list of all courses.
        """
        pass

    @abstractmethod
    def get_course_pair_weights(self) -> Callable[[Course, Course], float]:
        """
        Return weight for course pair.
        """
        pass

    def get_available_dates(self) -> Tuple[List[date], List[date]]:
        """
        :return: Tuple of two lists: a list of all available dates for moed a exams, and a list of all
        available dates for moed b exams.
        """
        return self.moedA_dates, self.moedB_dates
