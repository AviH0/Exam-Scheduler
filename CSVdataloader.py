from dataloader import Dataloader
import csv
from typing import List, Callable, Tuple
from datetime import date
from objects import *


class CSVdataloader(Dataloader):

    def __init__(self, dir: str, startA: date, startB: date, end: date, not_allowed: List[date]):

        super().__init__(startA, startB, end, not_allowed)
        super()._create_available_dates()

        self._courses = {}
        self._parse(dir)



    def _parse(self, dir: str):
        with open(dir) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for k, major_csv_row in enumerate(csv_reader):
                if k < 3:
                    continue
                major = Major(major_csv_row[0], k)
                for sem in Semester:
                    self._read_sem_k(sem, major_csv_row, major)

    def _read_sem_k(self, sem: Semester, major_csv_row: list, major: Major):

        sem_index = sem.value * 3 + 1  # from the structure of the csv file
        hova = major_csv_row[sem_index + 0].split(', ')
        bhirat_hova = major_csv_row[sem_index + 1].split(', ')
        bhira = major_csv_row[sem_index + 2].split(', ')

        # split will return [''] for an empty string input...
        if hova == ['']:
            hova = []
        if bhirat_hova == ['']:
            bhirat_hova = []
        if bhira == ['']:
            bhira = []

        self._add_course(hova, CourseType.HOVA, major, sem)
        self._add_course(bhirat_hova, CourseType.BHIRAT_HOVA, major, sem)
        self._add_course(bhira, CourseType.BHIRA, major, sem)

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

    @staticmethod
    def course_pair_weight_calc(c1: Course, c2: Course):
        common_majors = c1.get_common_majors(c2)
        cost = 0
        for major in common_majors:
            cost += c1.get_overlap_type_for_major(c2, major).value

        return cost

    def get_course_pair_weights(self) -> Callable[[Course, Course], float]:
        """
        Return weight for course pair.
        """
        return CSVdataloader.course_pair_weight_calc

    def get_available_dates(self) -> Tuple[List[date], List[date]]:
        """
        :return: Tuple of two lists: a list of all available dates for moed a exams, and a list of all
        available dates for moed b exams.
        """
        return self.moedA_dates, self.moedB_dates
