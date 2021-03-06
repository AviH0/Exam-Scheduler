from CSVdataloader import CSVdataloader
from solver import Solver
from datetime import date
from state import *
from genetic_solver import GeneticSolver
from StateLoader import StateLoader
import matplotlib.pyplot as plt


def func(prog):
    pass


def iter_changes(s, e):
    iters = [10, 100, 300, 500, 800, 1000]
    penalties = []

    for i in iters:
        sol = s.solve(func, i)
        penalty = e.evaluate(sol)
        print("iterations " + str(i) + ":  " + str(penalty))
        penalties.append(penalty)
    plt.plot(iters, penalties, 'b')
    plt.xlabel('Number of Iterations')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def pop_changes(e, dl):
    pop = [10, 20, 50, 60]
    penalties = []

    for p in pop:
        solver = GeneticSolver(dl, e, p)
        sol = solver.solve(func, 100)
        penalty = e.evaluate(sol)
        print("population " + str(p) + ":  " + str(penalty))
        penalties.append(penalty)
    plt.plot(pop, penalties, 'g')
    plt.xlabel('Population')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def p_muted_changes(e, dl):
    prob = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1]
    penalties = []

    for p in prob:
        solver = GeneticSolver(dl, e, p_mutate=p)
        sol = solver.solve(func, 100)
        penalty = e.evaluate(sol)
        print("population " + str(p) + ":  " + str(penalty))
        penalties.append(penalty)
    plt.plot(prob, penalties, 'r')
    plt.xlabel('Probabilities')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def main():
    dl = CSVdataloader("data/data2.csv", "data/courses_names_A.csv", date(2021, 1, 16), date(2021, 2, 11),
                       date(2021, 2, 13),
                       date(2021, 3, 4), [], YearSemester.SEM_A)
    evaluator = SumEvaluator(dl.get_course_pair_weights())

    solver = GeneticSolver(dl, evaluator)

    iter_changes(solver, evaluator)

    pop_changes(evaluator, dl)

    p_muted_changes(evaluator, dl)


if __name__ == "__main__":
    main()
