
from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from SAsolver import SAsolver

GENETIC_SOL = "genetic"
SA_SOL = "simulated_annealing"


def run_solver(major_data_path: str, courses_A_data_path: str, courses_B_data_path: str,
               sem_a_a_start, sem_a_a_end, sem_a_b_start, sem_a_b_end,
               sem_b_a_start, sem_b_a_end, sem_b_b_start, sem_b_b_end,
               forbidden_dates, solver_type, prog_call_back, iterations=None):



    loader_A = CSVdataloader(major_data_path, courses_A_data_path,
                             sem_a_a_start, sem_a_a_end, sem_a_b_start, sem_a_b_end, forbidden_dates,
                             YearSemester.SEM_A)
    loader_B = CSVdataloader(major_data_path, courses_B_data_path,
                             sem_b_a_start, sem_b_a_end, sem_b_b_start, sem_b_b_end, forbidden_dates,
                             YearSemester.SEM_B)

    evaluator_A = SumEvaluator(loader_A.get_course_pair_weights())
    evaluator_B = SumEvaluator(loader_B.get_course_pair_weights())

    if solver_type == GENETIC_SOL:
        if not iterations:
            iterations = 1000
        gen_solver_A = GeneticSolver(loader_A, evaluator_A)
        gen_solver_B = GeneticSolver(loader_B, evaluator_B)
        sol_state_A = gen_solver_A.solve(prog_call_back, iterations)
        sol_state_B = gen_solver_B.solve(prog_call_back, iterations)


    if solver_type == SA_SOL:
        if not iterations:
            iterations = 3000
        sa_solver_A = SAsolver(loader_A, evaluator_A, ((sem_a_a_start, sem_a_a_end),
                                                                           (sem_a_b_start, sem_a_b_end)))
        sa_solver_B = SAsolver(loader_B, evaluator_B, ((sem_b_a_start, sem_b_a_end),
                                                                           (sem_b_b_start, sem_b_b_end)))
        sol_state_A = sa_solver_A.solve(lambda x: prog_call_back(x/2), iterations=iterations)
        sol_state_B = sa_solver_B.solve(lambda x: prog_call_back((x+1)/2), iterations=iterations)

    else:
        raise NotImplemented

    return sol_state_A, sol_state_B
