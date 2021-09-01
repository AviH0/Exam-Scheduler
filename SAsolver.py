import copy
from datetime import date, timedelta
from typing import List, Set, Dict, Tuple, Iterable, Sequence
from solver import *
from dataloader import Dataloader
from objects import Course
from state import Evaluator, State
from random import sample, choice, uniform
from math import exp


SWAP_GENERATOR = "SWAP"
MOVE_ONE_GENERATOR = "MOVE_ONE"
MOVE_TWO_GENERATOR = "MOVE_TWO"
GENERATORS = [SWAP_GENERATOR, MOVE_TWO_GENERATOR, MOVE_ONE_GENERATOR]
DEFAULT_T0 = 1200
ITERATION_N = 7000
SUB_GROUP_N = [1, 2, 3]



class SAstate(State):

    def __init__(self, bounds: Tuple[Tuple[date, date], Tuple[date, date]],
                 courses_and_dates: Dict[Course, Tuple[date, date]] = None,
                 course_list: Iterable[Course] = None,
                 date_list: Tuple[Sequence[date], Sequence[date]] = None,
                 dates_possible: Set[date] = None):
        super(SAstate, self).__init__(courses_and_dates, course_list, date_list)
        self.course_list = [c for c in self.courses_dict.keys()]
        self.date_list = date_list
        self.bounds = bounds
        if not dates_possible:
            self.dates_possible = set()
            self.build_poss_dates()

        else:
            self.dates_possible = dates_possible

    def build_poss_dates(self):
        """
            Builds set of all dates in date list for later checking. This is done once at the begninning of the program and
            is passed from each state to state. 
        """
        # self.dates_possible = set()
        for moed in [0,1]:
            for date2add in self.date_list[moed]:
                self.dates_possible.add(date2add)


    def get_successor(self, sub_group_n: int, generator: str):
        """
            Creates successor by effecting (len(course_list) choose sub_group_n) courses through generator action
        type.
            Generator types:
                SWAP_GENERATOR - swaps courses test dates with a randomly chosen other course
                MOVE_TWO_GENERATOR - moves both courses test dates a day forwards or a day backwards if allowed
                MOVE_ONE_GENERATOR - moves one of a courses test dates a day forwards or a day backwards
        """
        orig_state = SAstate(bounds=self.bounds,
                             courses_and_dates={c: self.courses_dict[c] for c in self.courses_dict},
                             dates_possible=self.dates_possible)
        courses2move = sample(self.course_list, sub_group_n)
        for course in courses2move:

            # swaps both moed dates between two courses
            if generator == SWAP_GENERATOR:
                course2swap = choice(self.course_list)
                dates2save = self.courses_dict[course]
                self.courses_dict[course] = self.courses_dict[course2swap]
                self.courses_dict[course2swap] = dates2save

            # moves both of the moeds of the given course a day forwards or backwards
            elif generator == MOVE_TWO_GENERATOR:
                i = 0
                new_dates = 0
                while i < 100:
                    direction = choice([-1, 1])
                    dates = self.courses_dict[course]
                    new_dates = dates[0] + timedelta(days=direction), dates[1] + timedelta(days=direction)
                    if self.bounds[0][0] <= new_dates[0] <= self.bounds[0][1] and \
                            self.bounds[1][0] <= new_dates[1] <= self.bounds[1][1] and new_dates[1] - new_dates[
                        0] >= timedelta(days=21) and \
                        new_dates[0] in self.dates_possible and new_dates[1] in self.dates_possible:
                        break
                    i += 1
                if i < 100:
                    self.courses_dict[course] = new_dates

            # moves one of the moeds of the given course a day forwards or backwards
            elif generator == MOVE_ONE_GENERATOR:
                i = 0
                new_dates = 0
                dates = self.courses_dict[course]
                while i < 100:
                    direction = choice([-1, 1])
                    moed = choice([0, 1])
                    new_date = dates[moed] + timedelta(days=direction)
                    if moed == 0:
                        new_dates = (new_date, dates[1])
                    else:
                        new_dates = (dates[0], new_date)
                    if self.bounds[moed][0] <= new_date <= self.bounds[moed][1] and new_dates[1] - new_dates[
                        0] >= timedelta(days=21) and new_date in self.dates_possible:
                        break
                    i += 1
                if i < 100:
                    self.courses_dict[course] = new_dates

        return orig_state


class SAsolver(Solver):

    def __init__(self, loader: Dataloader, evaluator: Evaluator,
                 bounds: Tuple[Tuple[date, date], Tuple[date, date]]):
        super(SAsolver, self).__init__(loader, evaluator)
        self.state = SAstate(bounds=bounds,
                             course_list=loader.get_course_list(),
                             date_list=loader.get_available_dates())
        self.cur_pen = self.evaluator(self.state)
        self.course_list = loader.get_course_list()
        self.weights = loader.get_course_pair_weights()
        self.dates = loader.get_available_dates()
        self.bounds = bounds

    def solve(self, progress_func: Callable, T0=None, iterations=ITERATION_N, re_gen = None,
              stage_2_per = None, re_best = None) -> State:        
        
        """
            Finds an optimal solution by running iterations, where at each iteration a change is made
        to a state. If the change improves the state we always continue with the change and if not
        then at a decreasing probability we take it in order to escape local minimas. The type of change 
        made each iteration changes thoughout the code in order to ensure more that we escape local minimas
        in large drainage basins. We also return to the best state found every re_best iterations in order 
        to ensure that we don't accedently leave a global minima once reached. 
        """
        def reduce_T_lin(T: float) -> float:  # linear reduce by 1 for first stage (1000 iterations)
            if T > 200:
                T -= 1
            elif T > 20:  # linear reduce by our linear_reduce_val for second stage
                T -= linear_reduce_val
            else:
                T = T * 0.1  # geometric reduce for third and final stage. (hill climbing stage)
            return T

        # declare temperature / relocating values
        last_stage_per = 0.8 if stage_2_per is None else stage_2_per
        linear_reduce_val = 180 / (iterations * last_stage_per)
        re_gen_val = 2000 if re_gen is None else re_gen
        re_best_val = 1500 if re_best is None else re_best
        
        
        # Simulated Annealing algorithm
        T = T0 if T0 else DEFAULT_T0
        generator, subgroup_size = None, None
        best = self.state
        best_pen = float("inf")
        last_stage = iterations * last_stage_per
        for k in range(iterations):
            progress_func(k/iterations)
            T = reduce_T_lin(T)
            if k % re_gen_val == 0:
                generator = MOVE_ONE_GENERATOR if k > last_stage else choice(GENERATORS)
                subgroup_size = choice([1, 2]) if k > last_stage else choice(SUB_GROUP_N)

            # relocate back to best state found so far
            if k % re_best_val == 0 and k < last_stage:
                self.state = best

            # try something new
            orig_state = self.state.get_successor(subgroup_size, generator)
            old_pen = self.evaluator(orig_state)
            new_pen = self.evaluator(self.state)

            if new_pen < best_pen:  # update best so far
                best = self.state
                best_pen = new_pen
            if new_pen < old_pen:
                self.cur_pen = new_pen
                continue

            if T == 0:  # don't save if we are towards the end
                self.state = orig_state
                continue
            calc = exp(- abs(old_pen - new_pen) / T)
            if uniform(0, 1) < calc:
                continue
            self.state = orig_state

        return self.state
