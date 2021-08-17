import random
from abc import abstractmethod
from datetime import date
from typing import Dict, List, Tuple, Iterable, Sequence

from objects import *


class State:

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: List[Course] = None, date_list: Tuple[Sequence[date], Sequence[date]] = None,
                 keep_empty: bool = False):
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
        self.course_list = course_list
        self.date_list = date_list
        self.courses_dict: Dict[Course, Tuple[date, date]] = courses_and_dates
        if not courses_and_dates and not keep_empty:
            self.random_initialise()

    def random_initialise(self):  # TODO Random is almost always bad - at least enforce 21 days between aleph and bet
        self.courses_dict = dict()
        for c in self.course_list:
            self.courses_dict[c] = random.choice(self.date_list[0]), random.choice(self.date_list[1])

    def __repr__(self):
        str_rep = ""
        for course in self.courses_dict:
            str_rep += str(course)+ ":   "
            str_rep += str(self.courses_dict[course][0]) + ",  "
            str_rep += str(self.courses_dict[course][1]) + "\n"

        return str_rep

    def get_major_schedule_repr(self, major: Major, year_sem: YearSemester):
        repr_str = ""
        for sem in MajorSemester:
            if sem.value % 2 != year_sem.value - 1:
                continue
            repr_str += "____Semester No. " + str(sem.value + 1) + "____\n"
            sem_courses = major.get_sem_courses(sem)
            hova = []
            bhova = []
            bhira = []
            for course in sem_courses.keys():
                if sem_courses[course] == CourseType.HOVA:
                    hova.append(course)
                if sem_courses[course] == CourseType.BHIRAT_HOVA:
                    bhova.append(course)
                if sem_courses[course] == CourseType.BHIRA:
                    bhira.append(course)

            repr_str += "hova:   \n"
            for course in hova:
                dateA, dateB = self.courses_dict[course]
                repr_str += "      " + course.number + ":  " + str(dateA) + "  " + str(dateB) + "\n"

            repr_str += "bhova:   \n"
            for course in bhova:
                dateA, dateB = self.courses_dict[course]
                repr_str += "      " + course.number + ":  " + str(dateA) + "  " + str(dateB) + "\n"

            repr_str += "bhira:   \n"
            for course in bhira:
                dateA, dateB = self.courses_dict[course]
                repr_str += "       " + course.number + ":  " + str(dateA) + "  " + str(dateB) + "\n"

        return repr_str

class Evaluator:

    def __init__(self, course_pair_evaluate):
        self.course_pair_evalutor = course_pair_evaluate

    @abstractmethod
    def evaluate(self, state: State) -> float:
        pass

    def __call__(self, state: State, *args, **kwargs) -> float:
        return self.evaluate(state)


class SumEvaluator(Evaluator):

    def __init__(self, course_pair_evaluate):
        super().__init__(course_pair_evaluate)

    def evaluate(self, state: State) -> float:

        sum = 0

        # first check moed A and B distance
        for course in state.courses_dict:
            A_date, B_date = state.courses_dict[course]
            if abs((B_date - A_date).days) < 21:
                sum += 1000

        course_list = list(state.courses_dict.keys())

        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                course1, course2 = course_list[i], course_list[j]
                course1_dateA, course1_dateB = state.courses_dict[course1]
                course2_dateA, course2_dateB = state.courses_dict[course2]

                time_A, time_B = abs((course1_dateA - course2_dateA).days) + 0.1, abs((course1_dateB - course2_dateB).days) + 0.1

                course_distance = self.course_pair_evalutor(course1, course2)
                if course_distance == 0:
                    sum += 0
                else:
                    sum += course_distance * (1 / time_A) + course_distance * (1 / time_B)
        return sum






