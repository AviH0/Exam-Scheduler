from abc import abstractmethod
from datetime import date
from typing import Dict, Tuple

from objects import Course


class State:

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None):
        """
        Initialise a new state. Each state holds a dictionary where the keys are courses and the values are
        a tuple of dates (moed a and moed b).
        :param courses_and_dates: dictionary of courses. If None, will random initialise state. default: None
        """
        if courses_and_dates:
            self.courses_dict = courses_and_dates
        else:
            self.random_initialise()

    def random_initialise(self):
        pass


class Evaluator:

    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, state: State) -> float:
        pass
