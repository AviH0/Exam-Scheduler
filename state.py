import random
from abc import abstractmethod
from datetime import date, timedelta
from typing import Dict, List, Tuple, Iterable, Sequence, Mapping, Set
import csv

from objects import *


class State:

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: List[Course] = None, date_list: Tuple[List[date], List[date]] = None,
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

    def random_initialise(self):
        self.courses_dict = dict()
        for c in self.course_list:
            a_date = random.choice(self.date_list[0])
            possible_b_dates = []
            for b_date in self.date_list[1]:
                if (b_date - a_date).days >= MIN_DAYS_FROM_A_TO_B:
                    possible_b_dates.append(b_date)
            if not possible_b_dates:  # if no possible dates - an error may happen
                print(a_date)
            b_date = random.choice(possible_b_dates)
            self.courses_dict[c] = a_date, b_date

    def export_solution(self) -> Mapping[date, Iterable[Course]]:
        """
        Exports the solution represented by the state - returns a mapping from a date to courses,
         instead of course to date
        """

        solution_mapping: Dict[date, Set[Course]] = {}
        for course in self.courses_dict:
            date_A = self.courses_dict[course][0]
            date_B = self.courses_dict[course][1]

            if date_A not in solution_mapping:
                solution_mapping[date_A] = set()
            solution_mapping[date_A].add(course)

            if date_B not in solution_mapping:
                solution_mapping[date_B] = set()
            solution_mapping[date_B].add(course)

        return solution_mapping

    def save_to_csv(self, file_path):
        file = open(file_path, 'w+', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter=',')

        for course in self.courses_dict:
            csv_writer.writerow([course.name, course.number[:-2],
                                 str(self.courses_dict[course][0]), str(self.courses_dict[course][1])])
        file.close()

    def __repr__(self):
        str_rep = ""
        for course in self.courses_dict:
            str_rep += str(course)+ ":   "
            str_rep += str(self.courses_dict[course][0]) + ",  "
            str_rep += str(self.courses_dict[course][1]) + "\n"

        return str_rep

    def get_major_schedule_repr(self, major: Major, year_sem: YearSemester):
        """
        This function returns a string representation of the exam schedules of a certain major for semester A or B
        """
        repr_str = ""
        for sem in MajorSemester:
            if MajorSemester.get_year_semester(sem) != year_sem:
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
            repr_str = self._get_major_schedule_repr_helper(hova, repr_str)

            repr_str += "bhova:   \n"
            repr_str = self._get_major_schedule_repr_helper(bhova, repr_str)

            repr_str += "bhira:   \n"
            repr_str = self._get_major_schedule_repr_helper(bhira, repr_str)

        return repr_str

    def _get_major_schedule_repr_helper(self, courses: List[Course], repr_str: str):
        """
        Adds to the string representation the dates of the given courses.
        """
        for course in courses:
            if course in self.courses_dict:
                dateA, dateB = self.courses_dict[course]
                repr_str += "      " + course.number + ":  " + str(dateA) + "  " + str(dateB) + "\n"
            else:
                repr_str += "      " + course.number + ":  NoInfo\n"
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

        course_list = list(state.courses_dict.keys())

        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                course1, course2 = course_list[i], course_list[j]
                course1_dateA, course1_dateB = state.courses_dict[course1]
                course2_dateA, course2_dateB = state.courses_dict[course2]

                time_A, time_B = abs((course1_dateA - course2_dateA).days) + 0.1, abs(
                    (course1_dateB - course2_dateB).days) + 0.1

                course_distance = self.course_pair_evalutor(course1, course2)
                if course_distance == 0:
                    continue
                else:
                    sum += course_distance * (1 / time_A) + course_distance * (1 / time_B)
        return sum






