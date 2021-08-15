from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from CSsolver import CSsolver
from SAsolver import SAsolver


# class ExamScheduler:
#
#     def __init__(self, dataloader: Dataloader, solver: Solver):
#
#         pass


def main():
    dl = CSVdataloader("data/data.csv", date(2021, 7, 1), date(2021, 8, 1), date(2021,8,20), [])
    evaluator = SumEvaluator(dl.get_course_pair_weights())
    # solver = GeneticSolver(dl, evaluator)
    # sol = solver.solve(1000)
    solver = CSsolver(dl, evaluator)
    sol = solver.solve()
    majors_dict = dl.get_majors_dict()
    major = majors_dict["מדמח חד חוגי"]
    print(sol.get_major_schedule_repr(major))


if __name__ == "__main__":
    main()