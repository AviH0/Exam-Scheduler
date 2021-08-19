from datetime import date, timedelta
from typing import List, Set, Dict, Tuple, Iterable, Sequence

from solver import *
from dataloader import Dataloader
from objects import Course
from state import Evaluator, State
from random import sample, choice, uniform
from math import exp

"""
    Things left here:
        -  find faster way to update score then evaluating every time
        -  dates change
        -  find best values for T0 and ITERATION_N
        -  find best reduce function for T 
                -> currently is linear with 3,000 jumping steps and 7,000 hill descending steps
 """


SWAP_GENERATOR = "SWAP"
MOVE_ONE_GENERATOR = "MOVE_ONE"
MOVE_TWO_GENERATOR = "MOVE_TWO"
GENERATORS = [SWAP_GENERATOR, MOVE_TWO_GENERATOR, MOVE_ONE_GENERATOR]
DEFAULT_T0 = 3000
ITERATION_N = 10000
SUB_GROUP_N = 5


class SAstate(State):

    def __init__(self, courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: Iterable[Course] = None, date_list: Tuple[Sequence[date], Sequence[date]] = None):
        super(SAstate, self).__init__(courses_and_dates, course_list, date_list)
        self.course_list = self.courses_dict.keys()
        self.date_list = date_list

    def get_successor(self, sub_group_n: int, generator: str):
        # TODO: should we update the total score here? it would be faster since we won't have to recalculate everything
        # TODO: should we make sure we get a possible successor? hard constraints might be too easy to violate,
        #  giving us very high prob for wrong solutions and a waist of time
        orig_state = SAstate(courses_and_dates=self.courses_dict)
        courses2move = sample(self.course_list, sub_group_n)
        for course in courses2move:
            if generator == SWAP_GENERATOR:
                course2swap = choice(self.course_list)
                dates2save = self.courses_dict[course]
                self.courses_dict[course] = self.courses_dict[course2swap]
                self.courses_dict[course2swap] = dates2save
            elif generator == MOVE_TWO_GENERATOR:
                direction = choice([-1, 1])
                dates = self.courses_dict[course]
                self.courses_dict[course] = (dates[0] + timedelta(days=direction), dates[1] + timedelta(days=direction))
            elif generator == MOVE_ONE_GENERATOR:
                direction = choice([-1, 1])
                moed = choice([0,1])
                dates = self.courses_dict[course]
                if moed == 0:
                    self.courses_dict[course] = (dates[0] + timedelta(days=direction), dates[1])
                else:
                    self.courses_dict[course] = (dates[0], dates[1] + timedelta(days=direction))
        return orig_state
    # start of 2nd to do of only giving back solutions that match hard constraints
    # def check_hard_constraints(self, course_a, dates_a, course_b, dates_b) -> float:
    #     """Checks to make sure that swapping these courses """
    #     for course2comp in self.course_list:
    #         if course2comp == course_a or course2comp == course_b:
    #             continue
    #
    #
    # def swap_generator(self, course):
    #     for i in range(3):
    #         course2swap = choice(self.course_list)


class SAsolver(Solver):

    def __init__(self, loader: Dataloader, evaluator: Evaluator, sem: YearSemester):
        super(SAsolver, self).__init__(loader, evaluator, sem)
        self.state = SAstate()
        self.course_list = loader.get_course_list(sem)
        self.weights = loader.get_course_pair_weights()
        self.dates = loader.get_available_dates()

    def solve(self, T0 = None) -> State:

        def reduce_T_lin(T: float):
            T -= 1 if T > 1 else 0.0001
            return T

        T = T0 if T0 else DEFAULT_T0
        generator = None
        for k in range(ITERATION_N):
            T = reduce_T_lin(T)
            if k % 1000 == 0:
                generator = choice(GENERATORS)
            orig_state = self.state.get_successor(SUB_GROUP_N, generator)
            old_pen = self.evaluator(orig_state)
            new_pen = self.evaluator(self.state)
            if new_pen < old_pen:
                continue
            elif uniform(0, 1) < exp(-(abs(old_pen - new_pen))/ T):
                continue
            self.state = orig_state

        return self.state

