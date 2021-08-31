import csv
from objects import *
from typing import List, Callable, Tuple, Mapping, Set, Dict, FrozenSet, Union
import re
from state import State
from datetime import date, timedelta


class StateLoader:
    MoedA = 1
    MoedB = 2

    # TODO courses to add are courses we have "major info" on them. If we add courses to the state that we don't
    #  have info about - we can't evaluate the state...
    def __init__(self, state_file_dir: str, courses_to_add: List[Course], bounds=None):
        self.bounds = bounds
        self.courses_to_add_dict = {course.number[0:5]: course for course in courses_to_add}
        self.state_dict: Dict[Course, Tuple[date, date]] = {}

        if bounds:
            self.startA_date = bounds[0][0]
            self.endA_date = bounds[0][1]
            self.startB_date = bounds[1][0]
            self.endB_date = bounds[1][1]

        self._parse(state_file_dir)

    def _parse(self, dir: str):

        with open(dir, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for k, course_csv_row in enumerate(csv_reader):
                if k == 0 and not self.bounds:
                    self._parse_dates_range(course_csv_row)
                    continue
                if not course_csv_row:
                    continue
                course_num = course_csv_row[1]
                if course_num not in self.courses_to_add_dict:
                    continue

                dateA, dateB = self._parse_dates(course_csv_row)
                if dateA is None or dateB is None:
                    continue

                course_obj = self.courses_to_add_dict[course_num]

                self.state_dict[course_obj] = (dateA, dateB)

    def _parse_dates_range(self, csv_first_row):
        """
        The first row if the file contains the dates of moed A and B exams
        """
        startA = re.split("/", csv_first_row[0])
        endA = re.split("/", csv_first_row[1])
        startB = re.split("/", csv_first_row[2])
        endB = re.split("/", csv_first_row[3])

        self.startA_date = date(int(startA[2]), int(startA[0]), int(startA[1]))
        self.endA_date = date(int(endA[2]), int(endA[0]), int(endA[1]))
        self.startB_date = date(int(startB[2]), int(startB[0]), int(startB[1]))
        self.endB_date = date(int(endB[2]), int(endB[0]), int(endB[1]))

    def _parse_dates(self, csv_course_row):
        """
        Parses the dates of the moed A and B of some course - a course is represent by a row in the csv file
        """

        date_A_lst = re.split(r"[,/\-.\\]", csv_course_row[2])
        date_B_lst = re.split(r"[,/\-.\\]", csv_course_row[3])

        if len(date_A_lst) != 3 or len(date_B_lst) != 3:
            return None, None

        A_date = self._parse_dates_helper(date_A_lst, StateLoader.MoedA)
        B_date = self._parse_dates_helper(date_B_lst, StateLoader.MoedB)

        if A_date is None or B_date is None:
            return None, None
        return A_date, B_date

    def _parse_dates_helper(self, date_as_lst, moed):
        """
        Helps to parse a date. Checks if the date fits in the date range +- 3 days.
        Tries to switch between month and day if there is a problem - the data is far from perfect.
        """
        d = None
        dates_flexibility = timedelta(days=9)
        start_date = (self.startA_date if moed == StateLoader.MoedA else self.startB_date) - dates_flexibility
        end_date = (self.endA_date if moed == StateLoader.MoedA else self.endB_date) + dates_flexibility
        if len(date_as_lst[0]) == 4:
            y = date_as_lst[0]
            m = date_as_lst[1]
            d = date_as_lst[2]
            date_as_lst[0] = m
            date_as_lst[1] = d
            date_as_lst[2] = y

        if len(date_as_lst[2]) == 2:
            date_as_lst[2] = '20' + date_as_lst[2]
        try:
            d = date(int(date_as_lst[2]), int(date_as_lst[0]), int(date_as_lst[1]))
            if not (start_date <= d <= end_date):
                try:
                    d = date(int(date_as_lst[2]), int(date_as_lst[1]), int(date_as_lst[0]))
                    if not (start_date <= d <= end_date):
                        return None
                except ValueError as e:
                    return None

        except ValueError as e:
            try:
                d = date(int(date_as_lst[2]), int(date_as_lst[1]), int(date_as_lst[0]))
                if not (start_date <= d <= end_date):
                    return None

            except ValueError as e:
                return None
        return d

    def get_state(self):
        """
        Returns the read state.
        """
        return State(self.state_dict)
