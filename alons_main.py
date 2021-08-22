from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from StateLoader import StateLoader




# class ExamScheduler:
#
#     def __init__(self, dataloader: Dataloader, solver: Solver):
#
#         pass

def main():

    dl = CSVdataloader("data/data2.csv", date(2021, 7, 1), date(2021, 8, 1), date(2021, 8, 1),
                       date(2021,8,20), [], "data/courses_A.csv", "data/courses_B.csv")
    evaluator = SumEvaluator(dl.get_course_pair_weights())

    solver = GeneticSolver(dl, evaluator, YearSemester.SEM_A)
    sol = solver.solve(1000)

    sl = StateLoader("data/courses_A.csv", dl.get_course_list(YearSemester.SEM_A))
    human_sol = sl.get_state()

    print("Machine sol penalty: " + str(evaluator.evaluate(sol)))
    print("Human solution penalty: " + str(evaluator.evaluate(human_sol)))

    # majors_dict = dl.get_majors_dict()
    # major = majors_dict["מדמח חד חוגי"]
    # print(sol.get_major_schedule_repr(major, YearSemester.SEM_A))
    # print(human_sol.get_major_schedule_repr(major, YearSemester.SEM_A))




if __name__ == "__main__":
    main()