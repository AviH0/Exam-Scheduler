
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
BOUNDS_MOED_A = (date(2021, 7, 1), date(2021, 8, 1))
BOUNDS_MOED_B = (date(2021, 8, 1), date(2021,8,20))
BOUNDS = (BOUNDS_MOED_A,BOUNDS_MOED_B)

# class ExamScheduler:
#
#     def __init__(self, dataloader: Dataloader, solver: Solver):
#
#         pass


# checks solver ten times and builds results of avg penalties --> changes won't work unless changes is returned from
#       SAsolver.solve() and not just a state. To make this work swap highlight return lines in SAsolver.solve()
def test_10_times(dl: CSVdataloader, evaluator: Evaluator, vals= None):

    results = []
    for i in range(10):
        solver = SAsolver(dl, evaluator, YearSemester.SEM_A, BOUNDS)
        sol, changes = solver.solve(vals=vals)
        results.append([evaluator.evaluate(sol), changes])

    changes_avg = [0,0,0,0,0]
    places = [0,0,0]
    sum = 0
    for res in results:
        penalty = res[0]
        sum += penalty
        if penalty < 40000:
            places[0] += 1
        elif penalty < 45000:
            places[1] += 1
        else:
            places[2] += 1
        for i in range(5):
            changes_avg[i] += res[1][i]

    avg_penalty = sum/10
    for i in range(5):
        changes_avg[i] = changes_avg[i]/10

    return [avg_penalty, places, changes_avg]


# checks simulated annealing on many different values controlling search on graph
def run_sa_tests(dl: CSVdataloader, evaluator: Evaluator):
    ITER_N = [40, 50, 60]
    stage2_per = [0.66]
    re_gen = [300, 500]
    re_best = [1000, 5000]
    all_results = {}
    for s2p in stage2_per:
        print(f"s2p: {s2p}")
        for rg in re_gen:
            print(f"    rg: {rg}")
            for rb in re_best:
                print(f"        rb: {rb}")
                name = f"s2p: {s2p}, rg: {rg}, rb: {rb}"
                all_results[name] =test_10_times(dl=dl, evaluator=evaluator, vals=[s2p, rg, rb])

    for key in all_results.keys():
        print(f"{key}: {all_results[key]}")


# generic solver
def run_solver(solver_type: str, dl: CSVdataloader, evaluator: Evaluator) -> Tuple[Solver, State]:
    """Runs solver of type solver_type and returns an object of type Solver and an object of type State as the
    solution state that the requested solver outputs."""
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
    dl = CSVdataloader(major_data_dir="data/data2.csv", startA=BOUNDS_MOED_A[0], endA=BOUNDS_MOED_A[1],
                       startB=BOUNDS_MOED_B[0], endB=BOUNDS_MOED_B[1], not_allowed=[],
                       sem_A_courses_data_dir="data/courses_A.csv", sem_B_courses_data_dir="data/courses_B.csv")
    evaluator = SumEvaluator(dl.get_course_pair_weights())

    # changing the following value changes solvers being used in program.
    solver_type = SIM_AN_SOL  # change this to GENETIC_SOL to run with genetic solver

    solver, sol = run_solver(solver_type=solver_type, dl=dl, evaluator=evaluator)
    majors_dict = dl.get_majors_dict()
    major = majors_dict["מדמח חד חוגי"]
    print(sol.get_major_schedule_repr(major, YearSemester.SEM_A))
    print(evaluator.evaluate(sol))


if __name__ == "__main__":
    main()