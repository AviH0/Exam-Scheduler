from dataloader import Dataloader
import csv
from typing import List, Callable, Tuple, Mapping, Set, Dict, FrozenSet, Union
from datetime import date
from objects import *
import re


class CSVdataloader(Dataloader):

    def __init__(self, dir: str, startA: date, startB: date, end: date, not_allowed: List[date]):

        super().__init__(startA, startB, end, not_allowed)
        super()._create_available_dates()
        self.__course_pairs: Dict[Course, Dict[Course, float]] = dict()
        self._courses_A = {}
        self._courses_B = {}
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
                for sem in MajorSemester:
                    self._read_sem_k(sem, major_csv_row, major)

    def _read_sem_k(self, sem: MajorSemester, major_csv_row: list, major: Major):

        sem_index = sem.value * 3 + 1  # from the structure of the csv file
        hova = re.split("\s*,\s*|\s+", major_csv_row[sem_index + 0])
        bhirat_hova = re.split("\s*,\s*|\s+", major_csv_row[sem_index + 1])
        bhira = re.split("\s*,\s*|\s+", major_csv_row[sem_index + 2])

        hova = self._get_valid_course_num(hova)
        bhirat_hova = self._get_valid_course_num(bhirat_hova)
        bhira = self._get_valid_course_num(bhira)

        hova_courses_obj = self._add_and_create_courses(hova, CourseType.HOVA, major, sem)
        bhirat_hova_courses_obj = self._add_and_create_courses(bhirat_hova, CourseType.BHIRAT_HOVA, major, sem)
        bhira_courses_obj = self._add_and_create_courses(bhira, CourseType.BHIRA, major, sem)

        self._update_course_weight_dict(hova_courses_obj, hova_courses_obj, CourseType.HOVA, CourseType.HOVA)
        self._update_course_weight_dict(hova_courses_obj, bhirat_hova_courses_obj, CourseType.HOVA, CourseType.BHIRAT_HOVA)
        self._update_course_weight_dict(hova_courses_obj, bhira_courses_obj, CourseType.HOVA, CourseType.BHIRA)
        self._update_course_weight_dict(bhirat_hova_courses_obj, bhirat_hova_courses_obj, CourseType.BHIRAT_HOVA, CourseType.BHIRAT_HOVA)
        self._update_course_weight_dict(bhirat_hova_courses_obj, bhira_courses_obj, CourseType.BHIRAT_HOVA, CourseType.BHIRA)
        self._update_course_weight_dict(bhira_courses_obj, bhira_courses_obj, CourseType.BHIRA, CourseType.BHIRA)

    def _get_valid_course_num(self, courses_num_lst):
        """
        Given a list of course numbers (string) from the data, check if indeed these are valid course numbers.
        @return: a list of the valid course numbers.
        """
        correct_course_lst = []
        for i, courseNo in enumerate(courses_num_lst):
            courseNo = re.sub("\D+", '', courseNo)
            if len(courseNo) == 5:
                correct_course_lst.append(courseNo)
        return correct_course_lst

    def _add_and_create_courses(self, courses_num: List[str], type: CourseType, major: Major, sem: MajorSemester):
        """
        This function is given a list of course numbers (pure 5 digits), their semester (in range of 8 semester) in a
        given major, and their type.
        The function creates the courses objects, and adds them to the list of courses of semester A or B accordingly

        :param courses_num: The list of course numbers (5 digits)
        :param type: the type of the courses
        :param major: a major object of the courses' major
        :param sem: the sem No' of the courses
        :return: List of the courses object created
        """
        sem_in_year = YearSemester.SEM_A if sem.value % 2 == 0 else YearSemester.SEM_B
        courses_dict = self._courses_A if sem_in_year == YearSemester.SEM_A else self._courses_B

        courses_objects = []

        for course_num in courses_num:
            course_num_with_sem = course_num + "-" + str(sem_in_year.value)
            course = Course(course_num_with_sem, "no name")  # TODO extract the name

            if course_num in courses_dict:
                course = courses_dict[course_num]
            else:
                courses_dict[course_num] = course
            major.add_course(course, type, sem)
            course.add_major(major, sem, type)
            courses_objects.append(course)

        return courses_objects

    def _update_course_weight_dict(self, course_lst1, course_lst2, type1 : CourseType, type2 : CourseType):
        """
        This fucntion receives two list of courses which are taught in the same semester in some major, as well
        as their type in the semester (hova / bhirat hove / bhira). The function goes through all of the possible
        pairs between the two lists, and gives them a appropriate weight according to their types.
        """
        # TODO remove code duplicate
        penalty = CollisionTypes.get_col_type(type1, type2).value

        if type1 == type2: # equal types mean that the lists are the same

            for i in range(len(course_lst1)):
                for j in range(i + 1, len(course_lst2)):
                    c1 = course_lst1[i]
                    c2 = course_lst2[j]
                    c1_order = c1 if c1 > c2 else c2
                    c2_order = c2 if c2 < c1 else c1

                    if c1_order not in self.__course_pairs:
                        self.__course_pairs[c1_order] = {}

                    if c2_order not in self.__course_pairs[c1_order]:
                        self.__course_pairs[c1_order][c2_order] = penalty
                    else:
                        self.__course_pairs[c1_order][c2_order] += penalty

        else:
            for c1 in course_lst1:
                for c2 in course_lst2:
                    c1_order = c1 if c1 > c2 else c2
                    c2_order = c2 if c2 < c1 else c1

                    if c1_order not in self.__course_pairs:
                        self.__course_pairs[c1_order] = {}

                    if c2_order not in self.__course_pairs[c1_order]:
                        self.__course_pairs[c1_order][c2_order] = penalty
                    else:
                        self.__course_pairs[c1_order][c2_order] += penalty


    def get_course_list(self, sem: YearSemester) -> Union[List[Course], None]:
        """
        Return list of all courses.
        """
        if sem != YearSemester.SEM_A and sem != YearSemester.SEM_B:
            return None

        courses_dict_of_sem = self._courses_A if sem == YearSemester.SEM_A else self._courses_B
        return list(courses_dict_of_sem.values())

    def get_majors_dict(self):
        return self._majors_dict

    def course_pair_weight_calc(self, c1: Course, c2: Course):
        if c1 == c2:
            return CollisionTypes.NONE.value

        c1_order = c1 if c1 > c2 else c2
        c2_order = c2 if c2 < c1 else c1

        if c1_order not in self.__course_pairs:
            return CollisionTypes.NONE.value

        if c2_order not in self.__course_pairs[c1_order]:
            return CollisionTypes.NONE.value

        return self.__course_pairs[c1_order][c2_order]

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
