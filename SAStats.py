import matplotlib.pyplot as plt
from tqdm import tqdm

from CSVdataloader import CSVdataloader
from SAsolver import SAsolver
from state import *


def func(p):
    pass


def iter_changes(s, e):
    iters = [10, 100, 300, 500, 800, 1000, 2000, 5000, 10_000, 20_000, 40_000, 60_000]
    penalties = []

    for i in tqdm(iters):
        sol = s.solve(func, iterations=i)
        penalty = e.evaluate(sol)
        penalties.append(penalty)
    plt.plot(iters, penalties, 'b')
    plt.xlabel('Number of Iterations')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def initial_T_changes(s, e):
    T_values = [10, 100, 300, 500, 800, 1000, 1200, 2000, 5000]
    penalties = []

    for val in tqdm(T_values):
        sol = s.solve(func, T0=val, iterations=5000)
        penalty = e.evaluate(sol)
        penalties.append(penalty)
    plt.plot(T_values, penalties, 'r')
    plt.xlabel('Initial T Values')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def re_gener_changes(s, e):
    T_values = [10, 100, 300, 500, 800, 1000, 1200, 2000, 5000]
    penalties = []

    for val in tqdm(T_values):
        sol = s.solve(func, re_gen=val, iterations=7000)
        penalty = e.evaluate(sol)
        penalties.append(penalty)
    plt.plot(T_values, penalties, 'r')
    plt.xlabel('Re-Generate values')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def second_stage_changes(s, e):
    T_values = [0.33, 0.45, 0.5, 0.66, 0.8, 0.9]
    penalties = []

    for val in tqdm(T_values):
        sol = s.solve(func, stage_2_per=val, iterations=7000)
        penalty = e.evaluate(sol)
        penalties.append(penalty)
    plt.plot(T_values, penalties, 'r')
    plt.xlabel('Second Stage Percentage')
    plt.ylabel('Penalties')
    plt.yscale('log')
    plt.show()


def main():
    dl = CSVdataloader("data/data2.csv", "data/courses_names_A.csv", date(2021, 1, 16), date(2021, 2, 11),
                       date(2021, 2, 13),
                       date(2021, 3, 4), [], YearSemester.SEM_A)
    evaluator = SumEvaluator(dl.get_course_pair_weights())

    solver = SAsolver(dl, evaluator, ((date(2021, 1, 16), date(2021, 2, 11)), (date(2021, 2, 13),
                                                                               date(2021, 3, 4))))

    # iter_changes(solver, evaluator)

    # initial_T_changes(solver, evaluator)

    re_gener_changes(solver, evaluator)

    second_stage_changes(solver, evaluator)


if __name__ == '__main__':
    main()
