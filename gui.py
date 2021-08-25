import datetime
import tkinter as tk
from tkinter import Tk, Frame
from typing import Dict, Sequence
import tkinter.filedialog
from tkcalendar import DateEntry

from CSVdataloader import CSVdataloader
from agenda_cal import Agenda
from exam_scheduler import run_solver, GENETIC_SOL
from genetic_solver import GeneticSolver
from objects import YearSemester
from state import SumEvaluator

WINDOW_SIZE = '1280x800'
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
        self.cp_frame = Frame(self.root, borderwidth=2, relief=tk.GROOVE)

        cal_frame_label = tk.Label(self.root, text="Display Calendar", font=HEADER1_FONT)
        cal_frame_label.grid(row=0, column=1)
        self.cal_frame = Frame(self.root, borderwidth=2, width=700, height=600, relief=tk.GROOVE)
        self.currently_selected_date = tk.StringVar()
        self.agenda = Agenda(self.cal_frame, selectmode='day', textvariable=self.currently_selected_date, rightclick_cb=lambda event: self.on_calendar_rightclick(event), firstweekday="sunday", weekenddays=[7, 7])
        self.agenda.pack(fill='both', expand=True)

        self.build_cp_frame(self.cp_frame)
        self.cp_frame.grid(row=1, column=0, sticky='swe')

        self.cal_frame.grid(row=1, column=1)

        display_cp_frame_label = tk.Label(self.root, text="Display Settings", font=HEADER1_FONT)
        display_cp_frame_label.grid(row=0, column=3)
        self.display_cp_frame = Frame(self.root, borderwidth=2, relief=tk. GROOVE)
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
                majors_to_display = set(
                    filter(lambda x: self.__majors_to_display[x].get(), self.__majors_to_display.keys()))
                for d in self.solution:
                    for c in self.solution[d]:
                        if majors_to_display.intersection({m.major_name for m in c.get_common_majors(c)}):
                            self.agenda.calevent_create(d, str(c),
                                                        ["Exam"] + [m.major_name for m in
                                                                    c.get_common_majors(c)])

            check = tk.Checkbutton(root, variable=self.__majors_to_display[tag], text=tag,
                                   command=toggle_tag)
            check.pack(side=tk.TOP)

    def build_cp_frame(self, root: Frame):

        self.maj_file_input = WidgetWithLabel(root, "Majors Data File")
        self.maj_file_input.set_widget(SelectFileFrame, width=10)
        self.maj_file_input.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.sem_a_courses_file_input = WidgetWithLabel(root, "Semester A Courses File")
        self.sem_a_courses_file_input.set_widget(SelectFileFrame, width=10)
        self.sem_a_courses_file_input.pack(expand=True, fill=tk.BOTH)

        self.sem_b_courses_file_input = WidgetWithLabel(root, "Semester B Courses File")
        self.sem_b_courses_file_input.set_widget(SelectFileFrame, width=10)
        self.sem_b_courses_file_input.pack(expand=True, fill=tk.BOTH)

        self.sem_a_start_entry = WidgetWithLabel(root, "Semester A Exams start: ")
        self.sem_a_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_start_entry.pack(expand=True, fill=tk.X)

        self.sem_a_a_end_entry = WidgetWithLabel(root, "Semester A 1st round end: ")
        self.sem_a_a_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_a_end_entry.pack(expand=True, fill=tk.X)

        self.sem_a_b_start_entry = WidgetWithLabel(root, "Semester A 2nd round start: ")
        self.sem_a_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                            month=self.agenda.get_displayed_month()[0],
                                            year=self.agenda.get_displayed_month()[1])
        self.sem_a_b_start_entry.pack(expand=True, fill=tk.X)

        self.sem_a_b_end_entry = WidgetWithLabel(root, "Semester A 2nd round end: ")
        self.sem_a_b_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_b_end_entry.pack(expand=True, fill=tk.X)

        self.sem_b_start_entry = WidgetWithLabel(root, "Semester B Exams start: ")
        self.sem_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_start_entry.pack(expand=True, fill=tk.X)

        self.sem_b_a_end_entry = WidgetWithLabel(root, "Semester B 1st round end: ")
        self.sem_b_a_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_a_end_entry.pack(expand=True, fill=tk.X)

        self.sem_b_b_start_entry = WidgetWithLabel(root, "Semester B 2nd round start: ")
        self.sem_b_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                            month=self.agenda.get_displayed_month()[0],
                                            year=self.agenda.get_displayed_month()[1])
        self.sem_b_b_start_entry.pack(expand=True, fill=tk.X)

        self.sem_b_b_end_entry = WidgetWithLabel(root, "Semester B 2nd round end: ")
        self.sem_b_b_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_b_end_entry.pack(expand=True, fill=tk.X)

        button = tk.Button(root, text="Solve", width=20, command=lambda: self.run_solution())
        button.pack()

    def run_solution(self):
        dl_a = CSVdataloader(self.maj_file_input.widget.get_selected_filename(),
                             self.sem_a_start_entry.widget.get_date(),
                             self.sem_a_a_end_entry.widget.get_date(),
                             self.sem_a_b_start_entry.widget.get_date(),
                             self.sem_a_b_end_entry.widget.get_date(),
                             [],
                             self.sem_a_courses_file_input.widget.get_selected_filename(),
                             self.sem_b_courses_file_input.widget.get_selected_filename())
        evaluator_a = SumEvaluator(dl_a.get_course_pair_weights())
        solver, sol = run_solver(GENETIC_SOL, dl_a, evaluator_a)
        solution = solver.export_solution()
        self.agenda.see(self.sem_a_start_entry.widget.get_date())
        for d in solution:
            for c in solution[d]:
                self.agenda.calevent_create(d, str(c),
                                            ["Exam"])
        self.solution = solution
        self.build_display_cp_frame(self.display_cp_frame)

    def on_calendar_rightclick(self, event):
        # Create the menu options and bindings:
        top_menu = tk.Menu(event.widget, tearoff=0)
        sem_a_menu = tk.Menu(top_menu)
        sem_b_menu = tk.Menu(top_menu)
        top_menu.add_cascade(label="Set As Semester A:", menu=sem_a_menu)
        top_menu.add_separator()
        top_menu.add_cascade(label="Set As Semester B:", menu=sem_b_menu)

        sem_a_menu.add_command(label="Exams Start",
                         command=lambda: self.sem_a_start_entry.widget.set_date(self.currently_selected_date.get()))
        sem_a_menu.add_command(label="Exams 1st Round End",
                               command=lambda: self.sem_a_a_end_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_a_menu.add_command(label="Exams 2st Round Start",
                               command=lambda: self.sem_a_b_start_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_a_menu.add_command(label="Exams 2st Round End",
                               command=lambda: self.sem_a_b_end_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_a_menu.add_command(label="No Exams on this Date")

        sem_b_menu.add_command(label="Exams Start",
                               command=lambda: self.sem_b_start_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_b_menu.add_command(label="Exams 1st Round End",
                               command=lambda: self.sem_b_a_end_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_b_menu.add_command(label="Exams 2st Round Start",
                               command=lambda: self.sem_b_b_start_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_b_menu.add_command(label="Exams 2st Round End",
                               command=lambda: self.sem_b_b_end_entry.widget.set_date(
                                   self.currently_selected_date.get()))
        sem_b_menu.add_command(label="No Exams on this Date")

        top_menu.tk_popup(event.x_root, event.y_root)


class WidgetWithLabel(Frame):

    def __init__(self, master: tk.BaseWidget, label: str, *args, **kwargs):
        super(WidgetWithLabel, self).__init__(master, *args, **kwargs)
        self.label = tk.Label(self, text=label, justify=tk.LEFT)
        self.label.pack(side=tk.LEFT)#grid(row=0, column=0, sticky=tk.W)
        self.widget = None

    def set_widget(self, widget, *args, **kwargs):
        self.widget = widget(self, *args, **kwargs)
        self.widget.pack(side=tk.RIGHT)#grid(row=0, column=1, sticky=tk.E)

class SelectFileFrame(Frame):

    def __init__(self, master: tk.BaseWidget, dialog_title: str = "Choose file...", width=None, *args, **kwargs):
        super(SelectFileFrame, self).__init__(master, *args, **kwargs)
        if width:
            self.field = tk.Entry(self, width=width)
        else:
            self.field = tk.Entry(self)
        self.field.pack(side=tk.LEFT)
        self.browse_button = tk.Button(self, text="Browse...", command=lambda : self.browse())
        self.browse_button.pack()
        self.dialog_title = dialog_title

    def browse(self):
        filename = tk.filedialog.askopenfilename(parent=self.master, title=self.dialog_title)
        self.field.delete(0, "end")
        self.field.insert(0, filename)

    def get_selected_filename(self):
        return self.field.get()


if __name__ == '__main__':
    gui = ExamSchedulerGui()
