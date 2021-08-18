import datetime
import tkinter as tk
from tkinter import Tk, Frame
from typing import Dict, Sequence

from tkcalendar import DateEntry

from CSVdataloader import CSVdataloader
from agenda_cal import Agenda
from genetic_solver import GeneticSolver
from objects import YearSemester
from state import SumEvaluator

WINDOW_SIZE = '1280x600'
WINDOW_TITLE = 'Exam Scheduler'
HEADER2_FONT = ("Courier New", 16)
HEADER1_FONT = ("Courier New", 18, 'bold')
BODY_FONT = ("Courier New", 12)
BG = 'white'


class ExamSchedulerGui:

    def __init__(self, window_size=WINDOW_SIZE, window_title=WINDOW_TITLE):
        self.root = Tk()
        self.root.geometry(WINDOW_SIZE)
        self.root.title(WINDOW_TITLE)

        cp_frame_label = tk.Label(self.root, text="Setup", font=HEADER1_FONT)
        cp_frame_label.grid(row=0, column=0)
        self.cp_frame = Frame(self.root, borderwidth=2, relief=tk.RAISED)


        cal_frame_label = tk.Label(self.root, text="Display Calendar", font=HEADER1_FONT)
        cal_frame_label.grid(row=0, column=1)
        self.cal_frame = Frame(self.root, borderwidth=2, relief=tk.RAISED)
        self.agenda = Agenda(self.cal_frame, selectmode='none', firstweekday="sunday", weekenddays=[7, 7])
        self.agenda.pack(fill='both', expand=True)

        self.build_cp_frame(self.cp_frame)
        self.cp_frame.grid(row=1, column=0, sticky=tk.NSEW)

        self.cal_frame.grid(row=1, column=1)

        display_cp_frame_label = tk.Label(self.root, text="Display Settings", font=HEADER1_FONT)
        display_cp_frame_label.grid(row=0, column=3)
        self.display_cp_frame = Frame(self.root, borderwidth=2, relief=tk.RAISED)
        self.display_cp_frame.grid(row=1, column=3)
        self.__majors_to_display = dict()
        self.root.mainloop()

    def build_display_cp_frame(self, root: Frame):
        tags = self.agenda.tag_names()
        for tag in tags:
            self.__majors_to_display[tag] = tk.IntVar()
            def toggle_tag():
                self.agenda.calevent_remove(tag="Exam")
                self.agenda.update()
                majors_to_display = set(filter(lambda x: self.__majors_to_display[x].get(), self.__majors_to_display.keys()))
                for d in self.solution:
                    for c in self.solution[d]:
                        if majors_to_display.intersection({m.major_name for m in c.get_common_majors(c)}):
                            self.agenda.calevent_create(d, str(c),
                                                        ["Exam"] + [m.major_name for m in c.get_common_majors(c)])


            check = tk.Checkbutton(root, variable=self.__majors_to_display[tag], text=tag, command=toggle_tag)
            check.pack(side=tk.TOP)

    def build_cp_frame(self, root: Frame):

        # tk.Label(root, text="Choose Data File", justify=tk.LEFT)\
        #     .grid(row=0, column=0, padx=5, sticky=tk.W, pady=10)

        # self.data_file_input = tk.Entry(root)
        # self.data_file_input.config(width=10)
        self.data_file_input = WidgetWithLabel(root, "Choose Data File")
        self.data_file_input.set_widget(tk.Entry, width=10)
        self.data_file_input.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.sem_a_start_entry = WidgetWithLabel(root, "Semester A Exams start: ")
        self.sem_a_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_a_start_entry.pack(expand=True, fill=tk.X)

        self.sem_a_mid_entry = WidgetWithLabel(root, "Semester A 2nd round start: ")
        self.sem_a_mid_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_a_mid_entry.pack(expand=True, fill=tk.X)

        self.sem_a_end_entry = WidgetWithLabel(root, "Semester A exams end: ")
        self.sem_a_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_a_end_entry.pack(expand=True, fill=tk.X)

        self.sem_b_start_entry = WidgetWithLabel(root, "Semester A Exams start: ")
        self.sem_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_b_start_entry.pack(expand=True, fill=tk.X)

        self.sem_b_mid_entry = WidgetWithLabel(root, "Semester A 2nd round start: ")
        self.sem_b_mid_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_b_mid_entry.pack(expand=True, fill=tk.X)

        self.sem_b_end_entry = WidgetWithLabel(root, "Semester A exams end: ")
        self.sem_b_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7], month=self.agenda.get_displayed_month()[0], year=self.agenda.get_displayed_month()[1])
        self.sem_b_end_entry.pack(expand=True, fill=tk.X)

        button = tk.Button(root, text="Solve", width=20, command=lambda: self.run_solution())
        button.pack()

    def run_solution(self):
        dl = CSVdataloader("data/data2.csv", self.sem_a_start_entry.widget.get_date(),
                           self.sem_a_mid_entry.widget.get_date(), self.sem_a_end_entry.widget.get_date(),
                           [])
        evaluator = SumEvaluator(dl.get_course_pair_weights())
        solver = GeneticSolver(dl, evaluator, YearSemester.SEM_A, initial_population=5, p_mutate=0.3,
                               p_fittness_geom=0.6)
        # sol = solver.solve(1000)
        # solver = CSsolver(dl, evaluator)
        solver.solve(10, verbose=True)
        solution = solver.export_solution()
        self.agenda.see(self.sem_a_start_entry.widget.get_date())
        for d in solution:
            for c in solution[d]:
                self.agenda.calevent_create(d, str(c), ["Exam"] + [m.major_name for m in c.get_common_majors(c)])
        self.solution = solution
        self.build_display_cp_frame(self.display_cp_frame)

class WidgetWithLabel(Frame):

    def __init__(self, master: tk.BaseWidget, label: str, *args, **kwargs):
        super(WidgetWithLabel, self).__init__(master, *args, **kwargs)
        self.label = tk.Label(self, text=label, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.widget = None

    def set_widget(self, widget, *args, **kwargs):
        self.widget = widget(self, *args, **kwargs)
        self.widget.grid(row=0, column=1, sticky=tk.E)


if __name__ == '__main__':
    gui = ExamSchedulerGui()
