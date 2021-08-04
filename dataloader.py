from abc import abstractmethod
from datetime import date
from typing import List, Callable, Tuple

from objects import Course


class Dataloader:

    def __init__(self):
        pass

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

    @abstractmethod
    def get_available_dates(self) -> Tuple[List[date], List[date]]:
        """
        :return: Tuple of two lists: a list of all available dates for moed a exams, and a list of all
        available dates for moed b exams.
        """
        pass
