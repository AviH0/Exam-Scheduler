from dataloader import Dataloader
import csv
from typing import List, Callable, Tuple, Mapping, Set, Dict, FrozenSet
from datetime import date
from objects import *
import re


class CSVdataloader(Dataloader):

    def __init__(self, dir: str, startA: date, startB: date, end: date, not_allowed: List[date]):

        super().__init__(startA, startB, end, not_allowed)
        super()._create_available_dates()
        self.__course_pairs: Dict[Course, Dict[Course, float]] = dict()
        self._courses = {}
        self._majors_dict = {}

        self._parse(dir)

    def _parse(self, dir: str):
        with open(dir, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for k, major_csv_row in enumerate(csv_reader):
                if k < 3:
                    continue
                major = Major(major_csv_row[0], k)
                self._majors_dict[major_csv_row[0]] = major
                for sem in Semester:
                    self._read_sem_k(sem, major_csv_row, major)

    def _read_sem_k(self, sem: Semester, major_csv_row: list, major: Major):

        sem_index = sem.value * 3 + 1  # from the structure of the csv file
        hova = re.split("\s*,\s*", major_csv_row[sem_index + 0])
        bhirat_hova = re.split("\s*,\s*", major_csv_row[sem_index + 1])
        bhira = re.split("\s*,\s*", major_csv_row[sem_index + 2])

        hova = self._get_valid_course_num(hova)
        bhirat_hova = self._get_valid_course_num(bhirat_hova)
        bhira = self._get_valid_course_num(bhira)

        self._add_course(hova, CourseType.HOVA, major, sem)
        self._add_course(bhirat_hova, CourseType.BHIRAT_HOVA, major, sem)
        self._add_course(bhira, CourseType.BHIRA, major, sem)

    def _get_valid_course_num(self, courses_num_lst):
        correct_course_lst = []
        for i, courseNo in enumerate(courses_num_lst):
            courseNo = re.sub("\D+", '', courseNo)
            if len(courseNo) == 5:
                correct_course_lst.append(courseNo)
        return correct_course_lst

    def _add_course(self, courses_num: List[str], type: CourseType, major: Major, sem: Semester):
        """
        This function adds the courses of the current semester of the current major to the course list,
        as well updating the current Major object with its courses
        :param courses_num: The list of course numbers
        :param type: the type of the courses
        :param major: a major object of the courses' major
        :param sem: the sem No' of the courses
        :return: None
        """
        for course_num in courses_num:
            course = Course(course_num, "no name")  # TODO how to get it
            if course_num in self._courses:
                course = self._courses[course_num]
            else:
                self._courses[course_num] = course

            major.add_course(course, type, sem)
            course.add_major(major, sem, type)

    def get_course_list(self) -> List[Course]:
        """
        Return list of all courses.
        """
        return list(self._courses.values())

    def get_majors_dict(self):
        return self._majors_dict

    def course_pair_weight_calc(self, c1: Course, c2: Course):
        try:
            return self.__course_pairs[c1][c2]
        except KeyError:
            if c1 not in self.__course_pairs:
                self.__course_pairs[c1] = dict()

            common_majors = c1.get_common_majors(c2)
            cost = 0
            for major in common_majors:
                cost += c1.get_overlap_type_for_major(c2, major).value

            self.__course_pairs[c1][c2] = cost
            return cost

    def get_course_pair_weights(self) -> Callable[[Course, Course], float]:
        """
        Return weight for course pair.
        """
        return lambda c1, c2: self.course_pair_weight_calc(c1, c2)

    def get_available_dates(self) -> Tuple[List[date], List[date]]:
        """
        :return: Tuple of two lists: a list of all available dates for moed a exams, and a list of all
        available dates for moed b exams.
        """
        return super().get_available_dates()
