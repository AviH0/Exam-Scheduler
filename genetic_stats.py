from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from StateLoader import StateLoader


def func(prog):
    pass


def iter_changes(s, e):
    iters = [10, 100, 300, 500, 800, 1000]

    for i in iters:
        sol = s.solve(func, i)
        penalty = e.evaluate(sol)
        print("iterations " + str(i) + ":  " + str(penalty))


def pop_changes(e, dl):
    pop = [10, 20, 50, 60]
    for p in pop:
        solver = GeneticSolver(dl, e, p)
        sol = solver.solve(func, 100)
        penalty = e.evaluate(sol)
        print("population " + str(p) + ":  " + str(penalty))


def p_muted_changes(e, dl):
    prob = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]
    for p in prob:
        solver = GeneticSolver(dl, e, p_mutate=p)
        sol = solver.solve(func, 100)
        penalty = e.evaluate(sol)
        print("population " + str(p) + ":  " + str(penalty))

def main():

    dl = CSVdataloader("data/data2.csv", "data/courses_names_A.csv",  date(2021, 1, 16), date(2021, 2, 11), date(2021, 2, 13),
                       date(2021, 3, 4), [], YearSemester.SEM_A)
    evaluator = SumEvaluator(dl.get_course_pair_weights())



    solver = GeneticSolver(dl, evaluator)

    iter_changes(solver, evaluator)


    # sol = solver.solve(func, 1000, True)
    #
    # sl = StateLoader("data/courses_A.csv", dl.get_course_list())
    # human_sol = sl.get_state()
    #
    # print("Machine sol penalty: " + str(evaluator.evaluate(sol)))
    # print("Human solution penalty: " + str(evaluator.evaluate(human_sol)))
    #
    # majors_dict = dl.get_majors_dict()
    # major = majors_dict["מדמח חד חוגי"]
    # print(sol.get_major_schedule_repr(major, YearSemester.SEM_A))
    # print(human_sol.get_major_schedule_repr(major, YearSemester.SEM_A))


if __name__ == "__main__":
    main()