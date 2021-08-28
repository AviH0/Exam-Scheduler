from dataloader import Dataloader
import csv
from typing import List, Callable, Tuple, Mapping, Set, Dict, FrozenSet, Union
from datetime import date
from objects import *
import re


class CSVdataloader(Dataloader):

    def __init__(self, major_data_dir: str, courses_data_dir: str,
                 startA: date, endA: date, startB: date, endB: date, not_allowed: List[date],
                 sem: YearSemester):

        super().__init__(startA, endA, startB, endB, not_allowed)
        super()._create_available_dates()

        self.__course_pairs: Dict[Course, Dict[Course, float]] = dict()
        self.courses_with_exams_names: Dict[str: str] = {}    # courses with exams. Mapping course num to its name
        self._courses: Dict[str: Course] = {}         # dictionary of course number to objects
        self._majors_dict: Dict[str: Major] = {}        # mapping major name to major object
        self.sem = sem
        self._parse_course_list_files(courses_data_dir)
        self._parse_majors_data(major_data_dir)

    def _parse_course_list_files(self, _courses_data_dir: str):
        """
        The function reads the courses-list files, in order to get the number and names of the courses
        that require and exam.
        """
        with open(_courses_data_dir, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for course_row in csv_reader:
                course_num = course_row[1]
                course_name = course_row[0]
                self.courses_with_exams_names[course_num] = course_name

    def _parse_majors_data(self, dir: str):

        with open(dir, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for k, major_csv_row in enumerate(csv_reader):
                if k < 3:
                    continue
                major = Major(major_csv_row[0])
                self._majors_dict[major_csv_row[0]] = major
                for sem in MajorSemester:
                    if MajorSemester.get_year_semester(sem) == self.sem:
                        self._read_sem_k(sem, major_csv_row, major)

    def _read_sem_k(self, sem: MajorSemester, major_csv_row: list, major: Major):
        """
        Given a row from the csv file (representing a major) and a semester to read from the major the function:
            - Reads the courses of the semester in the major by their types (hova, hovat bhira, bhira).
            - Creates course objects for each course that has an exam, and updates the major object
            - Sets the types of collision of all possible pairs of these course in the currents major's semeter.
        """

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

        # Create all of the possible types of collision types for the current semester.
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
        Given a list of course numbers (5 digits), of some semester of some major and their type, the function:
            - Checks if the course requires an exam at all (this info is available from the courses-lists-files)
            - Create course objects out of these courses.
            - Update the given major object - adds the courses to the major object
        Finely it will return the list of the created course objects

        :param courses_num: The list of course numbers (5 digits)
        :param type: the type of the courses
        :param major: a major object of the courses' major
        :param sem: the sem No' of the courses
        :return: List of the courses object created
        """

        courses_objects = []

        for course_num in courses_num:

            # if course does not require an exam - do not add it.
            if course_num not in self.courses_with_exams_names:
                continue

            course_num_with_sem = course_num + "-" + str(self.sem.value)
            course = Course(course_num_with_sem, self.courses_with_exams_names[course_num])

            if course_num in self._courses:
                course = self._courses[course_num]
            else:
                self._courses[course_num] = course

            major.add_course(course, type, sem)
            course.add_major(major, sem, type)
            courses_objects.append(course)

        return courses_objects

    def _update_course_weight_dict(self, course_lst1, course_lst2, type1: CourseType, type2: CourseType):
        """
        This function receives two list of courses which are taught in the same semester in some major, as well
        as their type in the semester (hova / bhirat hove / bhira). The function goes through all of the possible
        pairs between the two lists, and gives them a appropriate weight according to their types.
        """
        penalty = CollisionTypes.get_col_type(type1, type2).value

        if type1 == type2:  # equal types mean that the lists are the same
            for i in range(len(course_lst1)):
                for j in range(i + 1, len(course_lst2)):
                    c1 = course_lst1[i]
                    c2 = course_lst2[j]
                    self._update_course_weight_dict_helper(c1, c2, penalty)
        else:
            for c1 in course_lst1:
                for c2 in course_lst2:
                    self._update_course_weight_dict_helper(c1, c2, penalty)

    def _update_course_weight_dict_helper(self, c1: Course, c2: Course, penalty: int):
        """
        This helper fucntion receives two courses and their collision types, and the given pair of courses
        and their penalty to the dictionary of the course-pair-penalty ass needed.
        """
        c1_order = c1 if c1 > c2 else c2
        c2_order = c2 if c2 < c1 else c1

        if c1_order not in self.__course_pairs:
            self.__course_pairs[c1_order] = {}

        if c2_order not in self.__course_pairs[c1_order]:
            self.__course_pairs[c1_order][c2_order] = penalty
        else:
            self.__course_pairs[c1_order][c2_order] += penalty

    def get_course_list(self) -> Union[List[Course], None]:
        """
        Returns list of the courses of the given semester (semester A or B)
        """
        return list(self._courses.values())

    def get_majors_dict(self):
        """
        Returns a dictionary of majors: {major_name (str) : Major_object}
        """
        return self._majors_dict

    def course_pair_weight_calc(self, c1: Course, c2: Course):
        """
        Calculates the cost of the collision of these who courses.
        return an integer which implies how far the courses should be scheduled relative to each other.
        """
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
