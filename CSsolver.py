from datetime import date, timedelta
from typing import List, Set, Dict, Tuple, Iterable, Sequence

from solver import *
from dataloader import Dataloader
from objects import Course
from state import Evaluator, State

MAX_DATE_DIFF = 10  # maximum amount of days between tests that we let courses effect each other
MAX_PENALTY = 1.0  # maximum penalty allowed between two courses.


class CSstate(State):

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: Iterable[Course] = None, date_list: Tuple[Sequence[date], Sequence[date]] = None,
                 keep_empty: bool = False):
        super(CSstate, self).__init__(courses_and_dates, course_list, date_list, keep_empty)
        self.course_list = course_list
        self.date_list = date_list

    def new_state(self, new_course: Course, new_dates: Tuple[date, date]):
        assert new_course in self.courses_dict
        new_courses_and_dates = self.courses_dict[::]
        new_courses_and_dates[new_course] = new_dates
        return CSstate(courses_and_dates=new_courses_and_dates, course_list=self.course_list, date_list=self.date_list)

    def is_pos_goal_state(self):
        """Checks if cur state is a possible placement (every course is included, at least 18 days between moed's)"""
        for course in self.course_list:
             if course not in self.courses_dict:
                 return False
             if self.courses_dict[course][1] - self.courses_dict[course][0] < 18:  # todo comp timedelta not int
                 return False
        return True


class CSsolver(Solver):
    """
        Class of solvers that build tests schedules according to constraint satisfaction backtracking algorithms.
    """
    def __init__(self, loader: Dataloader, evaluator: Evaluator):
        super(CSsolver, self).__init__(loader, evaluator)
        self.solutions = set()

    def solve(self) -> Set[State]:
        """
            Builds all possible schedules matching hard constraints.
                The hard constraints are: - 21 days in between tests
                                          - if the penalty between two tests of some two courses on some two dates
                                            is more then MAX_PENALTY (defined above)
        """
        courses_by_points = self._get_top_10({course: course.course_points for course in self.course_list},
                                             reverse=False)
        empty_state = CSstate(course_list=self.course_list, date_list=self.dates, keep_empty=True)
        empty_courses_penalties = {course: 0 for course in self.course_list}

        for course2start_with in courses_by_points:
            starting_state = empty_state.new_state(new_course=course2start_with, new_dates=(self.moed_a_dates[0],
                                                                              self.moed_b_dates[0]))
            self._backtracker(state=starting_state, solutions=set(),
                              courses_not_included=self._update_course_penalties(course2start_with,
                                                                                 empty_courses_penalties))
        return self.solutions

    def _update_course_penalties(self, new_course: Course,
                                 courses_not_included: Dict[Course, float]) -> Dict[Course, float]:
        """
            Updates dictionary of weights of courses not yet scheduled with the new course being scheduled.
        :param new_course: new course we want to schedule test for
        :param courses_not_included: courses that their tests have not yet been scheduled.
        :return: NEW updated dictionary of courses that have not yet been scheduled and their weights to add them to the
        schedule. (a new dictionary is returned for backtracking purposes)
        """
        new_course_dict = dict()
        for course2compare in courses_not_included:
            if course2compare != new_course:
                new_course_dict[course2compare] = courses_not_included[course2compare] +\
                                                  self.course_pair_evaluator((new_course, course2compare))

        return new_course_dict

    def _cal_penalty(self, state: CSstate, courses_included: Set[Course], new_course: Course,
                     new_dates: Tuple[date, date]) -> float:
        """
            Calculates the penalty of adding a test of some course on some two dates in the schedule.
        :param state: Current state with tests already scheduled.
        :param courses_included: Set of tests that their tests are already scheduled.
        :param new_course: Course we want to add to schedule.
        :param new_dates: Dates we want this new course to have tests on.
        :return: Float symbolizing the strain on the schedule by adding tests of this subject on these dates.
        """
        penalty = .0
        for course2compare in courses_included:
            for date2compare in state.courses_dict[course2compare]:
                for new_date in new_dates:
                    dates_diff = abs(date2compare - new_date) # check both if moedA of one is close to moedB of other
                    if dates_diff < MAX_DATE_DIFF:
                        cur_penalty = 1/dates_diff * self.course_pair_evaluator((new_course, course2compare))
                        penalty += cur_penalty if cur_penalty < MAX_PENALTY else 0
        return penalty

    def _get_top_10(self, some_dict: dict, reverse=True):
        """
            todo: find func that does this
            Returns top ten keys of dictionary with lowest values.
        """
        sorted_dict = sorted(some_dict.items(), key=lambda x: x[1], reverse=reverse)[:10]
        return [x[0] for x in sorted_dict]

    def _top_ten_dates2check(self, state: CSstate, courses_included: Set[Course],
                             new_course: Course) -> List[date]:
        """
            Finds the ten best dates for a given course to have it's tests on
        :param state: Current state with tests already scheduled.
        :param courses_included: Set of tests that their tests are already scheduled.
        :param new_course: Course we want to add to schedule.
        """
        dates_penalties = dict()
        for date in self.moed_a_dates:
            dates_penalties[date] = self._cal_penalty(state, courses_included, new_course,
                                                      (date, date+timedelta(days=21)))

        return self._get_top_10(dates_penalties)  # todo send with traverse =False? we want lowest pen days

    def _backtracker(self, state: CSstate, solutions: Set[State], courses_included: Set[Course] = None,
                    courses_not_included: Dict[Course, float] = None):
        """
            CSP algorithm. Backtracks through all possible solutions and returns ones that match constraints.
            General Build:
                with base case of a given state as a possible goal state (all tests scheduled while
                                                                          not violating any hard constraints)
                for given state - for 10 courses (not yet scheduled) with min penalty on 10 dates with min penalty
                            continue checking
        :param state: Current state with tests already scheduled.
        :param solutions: States that match hard constraints and all courses's tests are scheduled.
        :param courses_included: Set of tests that their tests are already scheduled.
        :param courses_not_included: courses that their tests have not yet been scheduled.

        """
        if state.is_pos_goal_state():
            self.solutions.add(state)
            return
        for course2add in self._get_top_10(courses_not_included):
            new_courses_not_included = self._update_course_penalties(course2add, courses_not_included)
            courses_included.add(course2add)
            for date2add in self._top_ten_dates2check(state, courses_included, course2add):
                self._backtracker(state.new_state(course2add, (date2add, date2add+timedelta(days=21))), solutions,
                                  courses_included, new_courses_not_included)
            courses_included.remove(course2add)







