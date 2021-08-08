import random
from abc import abstractmethod
from datetime import date
from typing import Dict, Tuple, Iterable, Sequence

from objects import Course


class State:

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: Iterable[Course] = None, date_list: Tuple[Sequence[date], Sequence[date]] = None):
        """
        Initialise a new state. Each state holds a dictionary where the keys are courses and the values are
        a tuple of dates (moed a and moed b).
        :param courses_and_dates: dictionary of courses. If None, course_list and date_list must not be None,
        and will random initialise state. default: None
        :param course_list: Iterable of all courses. Must not be None if courses_and_dates is None.
        default: None
        :param date_list: Tuple of Sequences of available dates for moed a and moed b. Must not be None if
        courses_and_dates is None. default: None
        """
        assert course_list or courses_and_dates
        self.courses_dict: Dict[Course, Tuple[date, date]] = courses_and_dates
        if not courses_and_dates:
            self.random_initialise(course_list, date_list)

    def random_initialise(self, course_list: Iterable[Course], date_list: Tuple[Sequence[date], Sequence[date]]):
        self.courses_dict = dict()
        for c in course_list:
            self.courses_dict[c] = random.choice(date_list[0]), random.choice(date_list[1])



class Evaluator:

    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State) -> float:
        pass

    def __call__(self, state: State, *args, **kwargs) -> float:
        return self.evaluate(state)
