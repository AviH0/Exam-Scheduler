
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
               forbidden_dates, solver_type, prog_call_back):

    loader_A = CSVdataloader(major_data_path, courses_A_data_path,
                             sem_a_a_start, sem_a_a_end, sem_a_b_start, sem_a_b_end, forbidden_dates,
                             YearSemester.SEM_A)
    loader_B = CSVdataloader(major_data_path, courses_B_data_path,
                             sem_b_a_start, sem_b_a_end, sem_b_b_start, sem_b_b_end, forbidden_dates,
                             YearSemester.SEM_B)

    evaluator_A = SumEvaluator(loader_A.get_course_pair_weights())
    evaluator_B = SumEvaluator(loader_B.get_course_pair_weights())

    if solver_type == GENETIC_SOL:
        gen_solver_A = GeneticSolver(loader_A, evaluator_A)
        gen_solver_B = GeneticSolver(loader_B, evaluator_B)
        sol_state_A = gen_solver_A.solve(prog_call_back, 10)
        sol_state_B = gen_solver_B.solve(prog_call_back, 10)
        return sol_state_A, sol_state_B

    if solver_type == SA_SOL:
        pass


if __name__ == "__main__":
    pass


# # checks solver ten times and builds results of avg penalties --> changes won't work unless changes is returned from
# #       SAsolver.solve() and not just a state. To make this work swap highlight return lines in SAsolver.solve()
# def test_10_times(dl: CSVdataloader, evaluator: Evaluator, vals= None):
#
#     results = []
#     for i in range(10):
#         solver = SAsolver(dl, evaluator, YearSemester.SEM_A, BOUNDS)
#         sol, changes = solver.solve(vals=vals)
#         results.append([evaluator.evaluate(sol), changes])
#
#     changes_avg = [0,0,0,0,0]
#     places = [0,0,0]
#     sum = 0
#     for res in results:
#         penalty = res[0]
#         sum += penalty
#         if penalty < 40000:
#             places[0] += 1
#         elif penalty < 45000:
#             places[1] += 1
#         else:
#             places[2] += 1
#         for i in range(5):
#             changes_avg[i] += res[1][i]
#
#     avg_penalty = sum/10
#     for i in range(5):
#         changes_avg[i] = changes_avg[i]/10
#
#     return [avg_penalty, places, changes_avg]
#
#
# # checks simulated annealing on many different values controlling search on graph
# def run_sa_tests(dl: CSVdataloader, evaluator: Evaluator):
#     ITER_N = [40, 50, 60]
#     stage2_per = [0.66]
#     re_gen = [300, 500]
#     re_best = [1000, 5000]
#     all_results = {}
#     for s2p in stage2_per:
#         print(f"s2p: {s2p}")
#         for rg in re_gen:
#             print(f"    rg: {rg}")
#             for rb in re_best:
#                 print(f"        rb: {rb}")
#                 name = f"s2p: {s2p}, rg: {rg}, rb: {rb}"
#                 all_results[name] =test_10_times(dl=dl, evaluator=evaluator, vals=[s2p, rg, rb])
#
#     for key in all_results.keys():
#         print(f"{key}: {all_results[key]}")
