import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Tk, Frame
from typing import Dict, Sequence
import tkinter.filedialog

import tkcalendar
from tkcalendar import DateEntry

from CSVdataloader import CSVdataloader
from agenda_cal import Agenda
from exam_scheduler import run_solver, GENETIC_SOL, ExamScheduler
from genetic_solver import GeneticSolver
from objects import YearSemester
from state import SumEvaluator

WINDOW_SIZE = '1280x800'
WINDOW_TITLE = 'Exam Scheduler'
HEADER2_FONT = ("Courier New", 16)
HEADER1_FONT = ("Courier New", 18, 'bold')
BODY_FONT = ("Courier New", 12)
BG = 'white'


class WidgetWithLabel(Frame):

    def __init__(self, master: tk.BaseWidget, label: str, *args, **kwargs):
        super(WidgetWithLabel, self).__init__(master, *args, **kwargs)
        self.label = tk.Label(self, text=label, justify=tk.LEFT)
        self.label.pack(side=tk.LEFT)  # grid(row=0, column=0, sticky=tk.W)
        self.widget = None

    def set_widget(self, widget, *args, **kwargs):
        self.widget = widget(self, *args, **kwargs)
        self.widget.pack(side=tk.RIGHT)  # grid(row=0, column=1, sticky=tk.E)


class ExamSchedulerGui:

    def __init__(self, window_size=WINDOW_SIZE, window_title=WINDOW_TITLE):
        self.root = Tk()
        self.root.geometry(WINDOW_SIZE)
        self.root.title(WINDOW_TITLE)

        self.__exam_scheduler = None

        cp_frame_label = tk.Label(self.root, text="Setup", font=HEADER1_FONT)
        cp_frame_label.grid(row=0, column=0)
        self.cp_frame = Frame(self.root, borderwidth=2, relief=tk.GROOVE)

        cal_frame_label = tk.Label(self.root, text="Display Calendar", font=HEADER1_FONT)
        cal_frame_label.grid(row=0, column=1)
        self.cal_frame = Frame(self.root, borderwidth=2, width=700, height=600, relief=tk.GROOVE)
        self.currently_selected_date = tk.StringVar()

        self.agenda = Agenda(self.cal_frame, selectmode='day', textvariable=self.currently_selected_date,
                             rightclick_cb=lambda event: self.on_calendar_rightclick(event),
                             firstweekday="sunday", selectbackground='yellow', selectforeground='black',
                             disabledselectbackground='yellow', disabledselectforeground='black',
                             weekenddays=[7, 7],
                             normalbackground='gray60')
        self.agenda.pack(fill='both', expand=True)

        self.build_cp_frame(self.cp_frame)
        self.cp_frame.grid(row=1, column=0, sticky='swe')

        self.cal_frame.grid(row=1, column=1)

        display_cp_frame_label = tk.Label(self.root, text="Display Settings", font=HEADER1_FONT)
        display_cp_frame_label.grid(row=0, column=3)
        self.display_cp_frame = Frame(self.root, borderwidth=2, relief=tk.GROOVE)
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

        load_frame = tk.LabelFrame(root, text="Load Data")
        load_frame.pack(side=tk.TOP, pady=50)

        self.maj_file_input = WidgetWithLabel(load_frame, "Majors Data File")
        self.maj_file_input.set_widget(SelectFileFrame, width=10)
        self.maj_file_input.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.sem_a_courses_file_input = WidgetWithLabel(load_frame, "Semester A Courses File")
        self.sem_a_courses_file_input.set_widget(SelectFileFrame, width=10)
        self.sem_a_courses_file_input.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.sem_b_courses_file_input = WidgetWithLabel(load_frame, "Semester B Courses File")
        self.sem_b_courses_file_input.set_widget(SelectFileFrame, width=10)
        self.sem_b_courses_file_input.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.__load_button = tk.Button(load_frame, text="Load", command=lambda: self.load_files)
        self.__load_button.pack(side=tk.RIGHT, padx=10, pady=15, ipadx=5, ipady=2)

        dates_frame = tk.LabelFrame(root, text="Setup Schedule")
        dates_frame.pack(side=tk.BOTTOM)

        self.sem_a_start_entry = WidgetWithLabel(dates_frame, "Semester A Exams start")
        self.sem_a_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_start_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_a_start_entry))
        self.sem_a_start_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_a_a_end_entry = WidgetWithLabel(dates_frame, "Semester A 1st round end")
        self.sem_a_a_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_a_end_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_a_a_end_entry))
        self.sem_a_a_end_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_a_b_start_entry = WidgetWithLabel(dates_frame, "Semester A 2nd round start")
        self.sem_a_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                            month=self.agenda.get_displayed_month()[0],
                                            year=self.agenda.get_displayed_month()[1])
        self.sem_a_b_start_entry.widget.bind('<<DateEntrySelected>>',
                                             lambda x: self.update_selected_dates(self.sem_a_b_start_entry))
        self.sem_a_b_start_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_a_b_end_entry = WidgetWithLabel(dates_frame, "Semester A 2nd round end")
        self.sem_a_b_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_a_b_end_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_a_b_end_entry))
        self.sem_a_b_end_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_b_start_entry = WidgetWithLabel(dates_frame, "Semester B Exams start")
        self.sem_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_start_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_b_start_entry))
        self.sem_b_start_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_b_a_end_entry = WidgetWithLabel(dates_frame, "Semester B 1st round end")
        self.sem_b_a_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_a_end_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_b_a_end_entry))
        self.sem_b_a_end_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_b_b_start_entry = WidgetWithLabel(dates_frame, "Semester B 2nd round start")
        self.sem_b_b_start_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                            month=self.agenda.get_displayed_month()[0],
                                            year=self.agenda.get_displayed_month()[1])
        self.sem_b_b_start_entry.widget.bind('<<DateEntrySelected>>',
                                             lambda x: self.update_selected_dates(self.sem_b_b_start_entry))
        self.sem_b_b_start_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.sem_b_b_end_entry = WidgetWithLabel(dates_frame, "Semester B 2nd round end")
        self.sem_b_b_end_entry.set_widget(DateEntry, firstweekday="sunday", weekenddays=[7, 7],
                                          month=self.agenda.get_displayed_month()[0],
                                          year=self.agenda.get_displayed_month()[1])
        self.sem_b_b_end_entry.widget.bind('<<DateEntrySelected>>',
                                           lambda x: self.update_selected_dates(self.sem_b_b_end_entry))
        self.sem_b_b_end_entry.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.__choose_solver = WidgetWithLabel(dates_frame, "Solver Algorithm")
        self.__choose_solver.set_widget(ttk.Combobox, values=["Genetic Algorithm", "Simulated Annealing"])
        self.__choose_solver.pack(expand=True, fill=tk.X, pady=5, padx=5)

        button = tk.Button(dates_frame, text="Solve", command=lambda: self.run_solution())
        button.pack(side=tk.RIGHT, padx=10, pady=15, ipadx=5, ipady=2)

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
        self.update_selected_dates(None, update_from_selection=False)

    def on_calendar_rightclick(self, event):
        # Create the menu options and bindings:
        top_menu = tk.Menu(event.widget, tearoff=0)
        sem_a_menu = tk.Menu(top_menu, tearoff=0)
        sem_b_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="Set As Semester A:", menu=sem_a_menu)
        top_menu.add_cascade(label="Set As Semester B:", menu=sem_b_menu)
        top_menu.add_separator()

        sem_a_menu.add_command(label="Exams Start",
                               command=lambda: self.update_selected_dates(self.sem_a_start_entry,
                                                                          update_from_selection=True))
        sem_a_menu.add_command(label="Exams 1st Round End",
                               command=lambda: self.update_selected_dates(self.sem_a_a_end_entry,
                                                                          update_from_selection=True))
        sem_a_menu.add_command(label="Exams 2nd Round Start",
                               command=lambda: self.update_selected_dates(self.sem_a_b_start_entry,
                                                                          update_from_selection=True))
        sem_a_menu.add_command(label="Exams 2nd Round End",
                               command=lambda: self.update_selected_dates(self.sem_a_b_end_entry,
                                                                          update_from_selection=True))

        sem_b_menu.add_command(label="Exams Start",
                               command=lambda: self.update_selected_dates(self.sem_b_start_entry,
                                                                          update_from_selection=True))
        sem_b_menu.add_command(label="Exams 1st Round End",
                               command=lambda: self.update_selected_dates(self.sem_b_a_end_entry,
                                                                          update_from_selection=True))
        sem_b_menu.add_command(label="Exams 2nd Round Start",
                               command=lambda: self.update_selected_dates(self.sem_b_b_start_entry,
                                                                          update_from_selection=True))
        sem_b_menu.add_command(label="Exams 2nd Round End",
                               command=lambda: self.update_selected_dates(self.sem_b_b_end_entry,
                                                                          update_from_selection=True))

        is_forbidden = tk.BooleanVar()
        is_forbidden.set(not not self.agenda.get_calevents(self.agenda.selection_get(), "forbidden"))

        top_menu.add_checkbutton(label="No Exams on this Date",
                                 command=lambda: self.forbid_date(is_forbidden.get()), variable=is_forbidden)

        top_menu.tk_popup(event.x_root, event.y_root)

    def update_selected_dates(self, date_entry: WidgetWithLabel, update_from_selection=False):

        self.agenda.calevent_remove(tag="date_config")
        if update_from_selection:
            date_entry.widget.set_date(self.currently_selected_date.get())

        date_a: datetime.date = self.sem_a_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_a_start_entry.label['text'], 'date_config')
        while date_a < self.sem_a_a_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['date_config', "1st_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_a_a_end_entry.label['text'], 'date_config')

        date_a: datetime.date = self.sem_a_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_a_b_start_entry.label['text'], 'date_config')
        while date_a < self.sem_a_b_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['date_config', "2nd_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_a_b_end_entry.label['text'], 'date_config')

        date_a: datetime.date = self.sem_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_b_start_entry.label['text'], 'date_config')
        while date_a < self.sem_b_a_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['date_config', "1st_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_b_a_end_entry.label['text'], 'date_config')

        date_a: datetime.date = self.sem_b_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_b_b_start_entry.label['text'], 'date_config')
        while date_a < self.sem_b_b_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['date_config', "2nd_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_b_b_end_entry.label['text'], 'date_config')

        self.update_tags()

    def update_tags(self):
        self.agenda.tag_config('1st_round', background='DodgerBlue2', foreground='red')
        self.agenda.tag_config('2nd_round', background='cyan2', foreground='green')
        self.agenda.tag_config('date_config', foreground='yellow')
        self.agenda.tag_config('forbidden', background='red', foreground='yellow')

    def forbid_date(self, is_forbidden: bool):
        date_to_forbid = self.agenda.selection_get()
        if is_forbidden:
            self.agenda.calevent_create(date_to_forbid, "No Exams", "forbidden")
        else:
            self.agenda.calevent_remove(date=date_to_forbid, tag='forbidden')
        self.update_tags()

    def load_files(self):
        self.__exam_scheduler = ExamScheduler(self.maj_file_input.widget.get_selected_filename(),
                                              self.sem_a_courses_file_input.widget.get_selected_filename(),
                                              self.sem_b_courses_file_input.widget.get_selected_filename())
        self.maj_file_input.widget.set_enabled(False)
        self.sem_a_courses_file_input.widget.set_enabled(False)
        self.sem_b_courses_file_input.widget.set_enabled(False)
        self.__load_button.configure(enabled=False)


class SelectFileFrame(Frame):

    def __init__(self, master: tk.BaseWidget, dialog_title: str = "Choose file...", width=None, *args,
                 **kwargs):
        super(SelectFileFrame, self).__init__(master, *args, **kwargs)
        if width:
            self.field = tk.Entry(self, width=width)
        else:
            self.field = tk.Entry(self)
        self.field.pack(side=tk.LEFT, padx=3)
        self.browse_button = tk.Button(self, text="Browse...", command=lambda: self.browse())
        self.browse_button.pack()
        self.dialog_title = dialog_title

    def browse(self):
        filename = tk.filedialog.askopenfilename(parent=self.master, title=self.dialog_title)
        self.field.delete(0, "end")
        self.field.insert(0, filename)

    def get_selected_filename(self):
        return self.field.get()

    def set_enabled(self, enabled: bool):
        self.field.configure(enabled=enabled)
        self.browse_button.configure(enabled=enabled)


if __name__ == '__main__':
    gui = ExamSchedulerGui()
