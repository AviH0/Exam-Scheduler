from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from SAsolver import SAsolver

GENETIC_SOL = "genetic"
SIM_AN_SOL = "simulated_annealing"
CS_SOL = "constraint_satisfaction"
CS_SA_SOL = "simulated_annealing_and_constraint_satisfaction"

# class ExamScheduler:
#
#     def __init__(self, dataloader: Dataloader, solver: Solver):
#
#         pass
BOUNDS_MOED_A = (date(2021, 7, 1), date(2021, 8, 1))
BOUNDS_MOED_B = (date(2021, 8, 1), date(2021,8,20))
BOUNDS = (BOUNDS_MOED_A,BOUNDS_MOED_B)

def run_solver(solver_type: str, dl: CSVdataloader, evaluator: Evaluator) -> Tuple[Solver, State]:

    solver, sol = None, None

    if solver_type == GENETIC_SOL:
        solver = GeneticSolver(dl, evaluator, YearSemester.SEM_A)
        sol = solver.solve(1000)
    elif solver_type == SIM_AN_SOL:
        solver = SAsolver(dl, evaluator, YearSemester.SEM_A, BOUNDS)
        sol = solver.solve()

    assert solver is not None and sol is not None
    return solver, sol


def main():
    dl = CSVdataloader(major_data_dir="data/data.csv", startA=BOUNDS_MOED_A[0], endA=BOUNDS_MOED_A[1],
                       startB=BOUNDS_MOED_B[0], endB=BOUNDS_MOED_B[1], not_allowed=[],
                       sem_A_courses_data_dir="data/courses_A.csv", sem_B_courses_data_dir="data/courses_B.csv")
    evaluator = SumEvaluator(dl.get_course_pair_weights())

    # changing the following value changes solvers being used in program.
    solver_type = SIM_AN_SOL

    solver, sol = run_solver(solver_type=solver_type, dl=dl, evaluator=evaluator)
    majors_dict = dl.get_majors_dict()
    major = majors_dict["מדמח חד חוגי"]
    print(sol.get_major_schedule_repr(major, YearSemester.SEM_A))
    print(evaluator.evaluate(sol))


if __name__ == "__main__":
    main()