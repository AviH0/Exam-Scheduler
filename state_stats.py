from typing import List
import matplotlib.pyplot as plt
from state import State, SumEvaluator
from objects import *
from CSVdataloader import CSVdataloader
from datetime import date
from genetic_solver import GeneticSolver
from StateLoader import StateLoader
import numpy as np


def _get_collisions_sol_update(output_dict, major, sem, c1, c2):
    if major in output_dict:
        if sem in output_dict[major]:
            output_dict[major][sem].append((c1, c2))
        else:
            output_dict[major][sem] = [(c1, c2)]
    else:
        output_dict[major] = {sem: [(c1, c2)]}


def get_collisions(state: State, moed: int, col_type: CollisionTypes):
    """
    Given a sate, moed (A=0, B=1), and a collision type to search for, will return a dictionary who's keys are
    majors, and the values are dicts of {sem: [(c1,c2),...]} where the course pairs are courses that have
    col_type collision in this major's semester.
    """
    courses_dates = state.courses_dict
    courses_list = list(courses_dates.keys())

    output_dict = {}

    for i in range(len(courses_list)):
        for j in range(i + 1, len(courses_list)):
            c1, c2 = courses_list[i], courses_list[j]
            c1_date, c2_date = courses_dates[c1][moed], courses_dates[c2][moed]
            if c1_date != c2_date:
                continue

            common_majors = c1.get_common_majors(c2)

            for major in common_majors:
                c1_sems_types_dict = {sem: _type for sem, _type in c1.get_majors()[major]}
                c2_sems_types_dict = {sem: _type for sem, _type in c2.get_majors()[major]}
                common_semesters = set(c1_sems_types_dict.keys()).intersection(set(c2_sems_types_dict.keys()))
                for sem in common_semesters:
                    type1 = c1_sems_types_dict[sem]
                    type2 = c2_sems_types_dict[sem]

                    cur_col_type = CollisionTypes.get_col_type(type1, type2)
                    if cur_col_type == col_type:
                        _get_collisions_sol_update(output_dict, major, sem, c1, c2)
    return output_dict


def get_average_break(state, major, course_types, moed):
    """
    Given a state, major, course type and moed, this function will retrun a list with 8 numbers, where
    each number is the average days between exams of the given type in the corresponding semester.
    Will return inf if there is only one exam, or no exams at all of the specified type.
    """

    averages_per_sem = []
    for sem in MajorSemester:
        courses_of_type = []
        sem_courses = major.get_sem_courses(sem)
        for course in sem_courses:
            if sem_courses[course] == course_types:
                courses_of_type.append(course)

        courses_of_type_dates = []
        for course in courses_of_type:
            try:
                courses_of_type_dates.append(state.courses_dict[course][moed])
            except KeyError:
                print(f"Could not find dates for course {course}")
        courses_of_type_dates.sort()

        if len(courses_of_type_dates) < 2:
            averages_per_sem.append('inf')
            continue

        sum_days = 0
        for i in range(1, len(courses_of_type_dates)):
            sum_days += (courses_of_type_dates[i] - courses_of_type_dates[i - 1]).days

        averages_per_sem.append(sum_days / (len(courses_of_type_dates) - 1))

    return averages_per_sem


def prog_dunc(som):
    pass


def get_coll_stats(sol: State, major: Major, moed: int):
    """
    Returns the number of collisions in the current major in the current state. The collisions of types
    HOVA_HOVA, HOVA_BHIRAT HOVA, BHIRAT HOVA_BHIRATHOVA, BHIRA_BHIRA.
    returns an array with the four numbers - number of collisions
    """
    num_coll = [0] * 4
    col_hova_hova = get_collisions(sol, moed, CollisionTypes.HOVA_HOVA)
    if major in col_hova_hova:
        for sem in col_hova_hova[major]:
            num_coll[0] += len(col_hova_hova[major][sem])

    col_hova_bhova = get_collisions(sol, moed, CollisionTypes.HOVA_BHOVA)
    if major in col_hova_bhova:
        for sem in col_hova_bhova[major]:
            num_coll[1] += len(col_hova_bhova[major][sem])

    col_bhova_bhova = get_collisions(sol, moed, CollisionTypes.BHOVA_BHOVA)
    if major in col_bhova_bhova:
        for sem in col_bhova_bhova[major]:
            num_coll[2] += len(col_bhova_bhova[major][sem])

    col_bhira_bhira = get_collisions(sol, moed, CollisionTypes.BHIRA_BHIRA)
    if major in col_bhira_bhira:
        for sem in col_bhira_bhira[major]:
            num_coll[3] += len(col_bhira_bhira[major][sem])

    return num_coll


def coll_stat_graph(majors: List[Major], sol_sem_a: State, moed: int, title=''):
    major_names = [m.major_name[::-1] for m in majors]
    hova_hova = []
    hova_bhova = []
    bhova_bhova = []
    bhira_bhira = []

    for major in majors:
        major_coll_a = get_coll_stats(sol_sem_a, major, moed)
        hova_hova.append(major_coll_a[0])
        hova_bhova.append(major_coll_a[1])
        bhova_bhova.append(major_coll_a[2])
        bhira_bhira.append(major_coll_a[3])

    barWidth = 0.25
    fig = plt.subplots(figsize=(12, 8))

    # Set position of bar on X axis
    br1 = np.arange(len(hova_hova))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]
    br4 = [x + barWidth for x in br3]

    # Make the plot
    plt.bar(br1, hova_hova, color='r', width=barWidth,
            edgecolor='grey', label='hova - hova')
    plt.bar(br2, hova_bhova, color='g', width=barWidth,
            edgecolor='grey', label='hova - bhirat hova')
    plt.bar(br3, bhova_bhova, color='b', width=barWidth,
            edgecolor='grey', label='bhirat hova - bhirat  hova')
    plt.bar(br4, bhira_bhira, color='y', width=barWidth,
            edgecolor='grey', label='bhira bhira')

    # Adding Xticks
    plt.xlabel('Major', fontweight='bold', fontsize=15)
    plt.ylabel('Collisions', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(hova_hova))],
              major_names,  rotation=45, fontsize=6)
    plt.title(title)
    plt.legend()
    plt.show()


def _get_average_without_inf(lst):
    counter = 0
    sum = 0
    for n in lst:
        if n != 'inf':
            counter += 1
            sum += n
    return sum / counter if counter > 0 else 0


def get_break_stats_graph(sol: State, majors: List[Major], moed: int, title=''):
    hova_avg = []
    bhova_avg = []
    bhira_avg = []

    major_names = [m.major_name[::-1] for m in majors]

    for major in majors:
        hova = get_average_break(sol, major, CourseType.HOVA, moed)
        bhova = get_average_break(sol, major, CourseType.BHIRAT_HOVA, moed)
        bhira = get_average_break(sol, major, CourseType.BHIRA, moed)

        hova_avg_break = _get_average_without_inf(hova)
        bhova_avg_break = _get_average_without_inf(bhova)
        bhira_avg_break = _get_average_without_inf(bhira)

        hova_avg.append(hova_avg_break)
        bhova_avg.append(bhova_avg_break)
        bhira_avg.append(bhira_avg_break)

    barWidth = 0.25
    fig = plt.subplots(figsize=(12, 8))

    # Set position of bar on X axis
    br1 = np.arange(len(hova_avg))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]

    # Make the plot
    plt.bar(br1, hova_avg, color='r', width=barWidth,
            edgecolor='grey', label='hova')
    plt.bar(br2, bhova_avg, color='g', width=barWidth,
            edgecolor='grey', label='bhirat hova')
    plt.bar(br3, bhira_avg, color='b', width=barWidth,
            edgecolor='grey', label='bhira')


    # Adding Xticks
    plt.xlabel('Major', fontweight='bold', fontsize=15)
    plt.ylabel('avg break', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(hova_avg))],
               major_names, rotation=45, fontsize=6)
    plt.title(title)

    plt.legend()
    plt.show()




def main():
    ################################
    #  ALWAYS COMPARES IN SEMESTER A OR B. CANT DO BOTH!!!
    # THAT IS BECAUSE IT DEPENDS ON DATA LOADER WHICH LOADS ONE SEMESTER AT A TIME
    ####################################
    dl = CSVdataloader("data/data4.csv", "data/courses_names_A.csv",
                       date(2022, 1, 16), date(2022, 2, 11), date(2022, 2, 15), date(2022, 3, 4),
                       [], YearSemester.SEM_A)

    majors = dl.get_majors_dict().values()
    # Get average "break" between exams graph.
    # The graph tells the average days between hova, hovat bhira and bhira exams for each major

    # human solution extraction:
    sl = StateLoader("data/sem_A_sol_human.csv", dl.get_course_list())
    human_sol = sl.get_state()
    get_break_stats_graph(human_sol, majors, 0, title=f"Semester A Human Solution")
    coll_stat_graph(majors, human_sol, 0, title=f"Semester A Human Solution")

    sa_sl = StateLoader("data/SA3000SEM_A.csv", dl.get_course_list(), bounds=((dl.startA, dl.endA), (dl.startB, dl.endB)))
    sa_sol = sa_sl.get_state()
    get_break_stats_graph(sa_sol, majors, 0, title=f"Semester A Solution with SA")
    coll_stat_graph(majors, sa_sol, 0, title=f"Semester A Solution with SA")

    gen_sl = StateLoader("data/GEN1000SEM_A.csv", dl.get_course_list(),
                        bounds=((dl.startA, dl.endA), (dl.startB, dl.endB)))
    gen_sol = gen_sl.get_state()
    get_break_stats_graph(gen_sol, majors, 0, title=f"Semester A Solution with Genetic")
    coll_stat_graph(majors, gen_sol, 0, title=f"Semester A Solution with Genetic")

    dl = CSVdataloader("data/data4.csv", "data/courses_names_B.csv",
                       date(2022, 6, 26), date(2022, 7, 27), date(2022, 7, 28), date(2022, 8, 19),
                       [], YearSemester.SEM_B)

    majors = dl.get_majors_dict().values()

    # human solution extraction:
    sl = StateLoader("data/sem_B_sol_human.csv", dl.get_course_list())
    human_sol = sl.get_state()
    get_break_stats_graph(human_sol, majors, 0, title=f"Semester B Human Solution")
    coll_stat_graph(majors, human_sol, 0, title=f"Semester B Human Solution")

    sa_sl = StateLoader("data/SA3000SEM_B.csv", dl.get_course_list(),
                        bounds=((dl.startA, dl.endA), (dl.startB, dl.endB)))
    sa_sol = sa_sl.get_state()
    get_break_stats_graph(sa_sol, majors, 0, title=f"Semester B Solution with SA")
    coll_stat_graph(majors, sa_sol, 0, title=f"Semester B Solution with SA")

    gen_sl = StateLoader("data/GEN1000SEM_B.csv", dl.get_course_list(),
                         bounds=((dl.startA, dl.endA), (dl.startB, dl.endB)))
    gen_sol = gen_sl.get_state()
    get_break_stats_graph(gen_sol, majors, 0, title=f"Semester B Solution with Genetic")
    coll_stat_graph(majors, gen_sol, 0, title=f"Semester B Solution with Genetic")

    # Get the graph represents the number of collisions in majors between different types of courses
    # Does it only for semester A courses (because that is the data that was provided by the data loader...)


if __name__ == "__main__":
    main()
