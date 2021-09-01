import asyncio
import contextvars
import functools
import threading
from asyncio import events
import datetime
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Tk, Frame
from typing import Dict, Sequence, List
from tkinter.messagebox import showerror
from tkinter.simpledialog import askstring
import tkinter.filedialog
from tkcalendar import DateEntry
from ttkwidgets import CheckboxTreeview

from CSVdataloader import CSVdataloader
from agenda_cal import Agenda
from dataloader import No21DaysOfMoedBException
from scheduler import run_solver, GENETIC_SOL, SA_SOL
from genetic_solver import GeneticSolver
from objects import YearSemester, Major, MajorSemester
from state import SumEvaluator, State

EXAMS_A_TAG = "Exams_A"

EXAMS_B_TAG = "Exams_B"

HARD_CODED_EXAMS_TAG = 'hard_coded_exams'

NO_EXAMS_TAG = 'forbidden'

DATES_INFO_TAG = 'DATES_INFO_TAG'

MOADEI_B_TAG = '2nd_round'

MOADEI_A_TAG = '1st_round'

WINDOW_SIZE = '1280x800'
WINDOW_TITLE = 'Exam Scheduler'
HEADER2_FONT = ("Courier New", 16)
HEADER1_FONT = ("Courier New", 18, 'bold')
BODY_FONT = ("Courier New", 12)
BG = 'white'

SOLVER_NAMES = {"Genetic Algorithm": GENETIC_SOL, "Simulated Annealing": SA_SOL}


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
        self.root = tk.Tk()
        self.root.geometry(window_size)
        self.root.title(window_title)

        self.__forbidden_dates: List[datetime.date] = []
        self.__majors_to_display: Dict[Major, Dict[MajorSemester, tk.BooleanVar]] = dict()

        self.__show_names = tk.BooleanVar()

        self.__solver_thread = None

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


        self.display_cp_frame = Frame(self.root, borderwidth=2, relief=tk.GROOVE)
        self.root.mainloop()

    def build_display_cp_frame(self, root: Frame, sol_a, sol_b):

        checklist_frame = tk.Frame(root, borderwidth=2, relief=tk.GROOVE)
        checklist = CheckboxTreeview(checklist_frame)
        sb = ttk.Scrollbar(checklist_frame)
        sb.configure(command=checklist.yview)
        checklist.configure(yscrollcommand=sb.set)

        checklist.pack(side=tk.LEFT, expand=True, fill='y')
        sb.pack(expand=True, fill='y')

        def toggle(major, sem):
            self.root.update()
            self.__majors_to_display[major][sem].set(checklist.tag_has("checked", item=f"{major.major_name}.{sem.name}"))
            self.__show_solution(sol_a, EXAMS_A_TAG)
            self.__show_solution(sol_b, EXAMS_B_TAG)

        def toggle_major(major):
            self.root.update()
            for sem in self.__majors_to_display[major]:
                self.__majors_to_display[major][sem].set(checklist.tag_has("checked", item=f"{major.major_name}.{sem.name}"))
            self.__show_solution(sol_a, EXAMS_A_TAG)
            self.__show_solution(sol_b, EXAMS_B_TAG)


        for i, maj in enumerate(self.__majors_to_display):
            checklist.insert("", "end", f"{maj.major_name}", text=f"{maj.major_name}", tags=["checked", maj.major_name])
            checklist.tag_bind(maj.major_name, "<1>", lambda x, maj=maj: self.root.after_idle(toggle_major, maj))
            for j, sem in enumerate(self.__majors_to_display[maj]):
                checklist.insert(f"{maj.major_name}", "end", f"{maj.major_name}.{sem.name}", text=f"{sem.name}", tags=["checked", f"{maj.major_name}.{sem.name}"])
                checklist.tag_bind(f"{maj.major_name}.{sem.name}", "<1>", lambda x, maj=maj, sem=sem: self.root.after_idle(toggle, maj, sem))

        checklist_frame.grid(row=0, column=0, rowspan=5, sticky=tk.NS)


        jump_frame = tk.LabelFrame(root, text="Calendar view jump")
        tk.Button(jump_frame, text="Jump to Semester A",
                  command=lambda: self.agenda.see(self.sem_a_start_entry.widget.get_date())).pack(pady=5)
        tk.Button(jump_frame, text="Jump to Semester B",
                  command=lambda: self.agenda.see(self.sem_b_start_entry.widget.get_date())).pack(pady=5)
        jump_frame.grid(row=0, column=2, stick='new')

        def save_sol(sol: State):
            filename = tkinter.filedialog.asksaveasfilename()
            if filename:
                sol.save_to_csv(filename)

        show_names = tk.Checkbutton(root, text="Show Course Names", variable=self.__show_names)
        show_names.grid(row=1, column=2, sticky=tk.E)

        self.__show_names.trace_add('write', lambda x, y, z: (self.__show_solution(sol_a, EXAMS_A_TAG),
                                                     self.__show_solution(sol_b, EXAMS_B_TAG)))

        save_frame = tk.LabelFrame(root, text="Save Schedule")
        tk.Button(save_frame, text="Save Semester A Schedule",
                  command=lambda: save_sol(sol_a)).pack(pady=5)
        tk.Button(save_frame, text="Save Semester B Schedule",
                  command=lambda: save_sol(sol_b)).pack(pady=5)
        save_frame.grid(row=2, column=2, stick='swe')

        def reset():
            self.agenda.calevent_remove(tag=EXAMS_A_TAG)
            self.agenda.calevent_remove(tag=EXAMS_B_TAG)
            self.agenda.update()
            self.display_cp_frame.grid_remove()
            self.cp_frame.grid(row=1, column=0)

        tk.Button(root, text="Reset",
                  command=reset).grid(row=3, column=2, sticky=tk.SE, pady=5)

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

        # self.__load_button = tk.Button(load_frame, text="Load", command=lambda: self.load_files)
        # self.__load_button.pack(side=tk.RIGHT, padx=10, pady=15, ipadx=5, ipady=2)

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
        self.__choose_solver.widget.current(0)
        self.__choose_solver.pack(expand=True, fill=tk.X, pady=5, padx=5)


        self.__choose_iterations =  WidgetWithLabel(dates_frame, "Number of Iterations (0 for default)")
        self.__choose_iterations.set_widget(ttk.Spinbox, from_=0, to=100_000)
        self.__choose_iterations.pack(expand=True, fill=tk.X, pady=5, padx=5)

        self.__solve_button = tk.Button(dates_frame, text="Solve", command=self.run_solution)
        self.__solve_button.pack(side=tk.RIGHT, padx=10, pady=15, ipadx=5, ipady=2)

        self.__prog_bar_frame = tk.Frame(dates_frame)
        self.__prog_bar_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=15)

    def run_solution(self):
        self.__solve_button.configure(state=tk.DISABLED)
        pb = ttk.Progressbar(self.__prog_bar_frame, length=100, mode='determinate', orient='horizontal')

        def update(current_progress):
            pb['value'] = current_progress * 100
            self.root.update()

        def run():
            try:
                kwargs = dict()
                iterations = int(self.__choose_iterations.widget.get())
                if iterations:
                    kwargs['iterations'] = iterations
                sol_a, sol_b = run_solver(self.maj_file_input.widget.get_selected_filename(),
                                          self.sem_a_courses_file_input.widget.get_selected_filename(),
                                          self.sem_b_courses_file_input.widget.get_selected_filename(),
                                          self.sem_a_start_entry.widget.get_date(),
                                          self.sem_a_a_end_entry.widget.get_date(),
                                          self.sem_a_b_start_entry.widget.get_date(),
                                          self.sem_a_b_end_entry.widget.get_date(),
                                          self.sem_b_start_entry.widget.get_date(),
                                          self.sem_b_a_end_entry.widget.get_date(),
                                          self.sem_b_b_start_entry.widget.get_date(),
                                          self.sem_b_b_end_entry.widget.get_date(),
                                          self.__forbidden_dates,
                                          SOLVER_NAMES[self.__choose_solver.widget.get()], update, **kwargs)
                pb.destroy()
                self.__solve_button.configure(state=tk.NORMAL)
                self.show_solutions(sol_a, sol_b)
            except No21DaysOfMoedBException:
                showerror("Error!", "Selected dates do not include 21 days between the end of 1st round "
                                    "and the end of 2nd round. Please retry with different dates.")
                pb.destroy()
                self.__solve_button.configure(state=tk.NORMAL)

        pb.pack(fill=tk.BOTH, expand=True)
        self.__solver_thread = threading.Thread(target=run).start()

    def __show_solution(self, sol, tag):
        self.agenda.calevent_remove(tag=tag)
        for date, courses in sol.export_solution().items():
            for c in courses:
                course_flag = False
                for maj, info in c.get_majors().items():
                    if maj not in self.__majors_to_display:
                        self.__majors_to_display[maj] = dict()
                    for i in info:
                        if i[0] not in self.__majors_to_display[maj]:
                            self.__majors_to_display[maj][i[0]] = tk.BooleanVar(value=True)
                        if self.__majors_to_display[maj][i[0]].get():
                            course_flag = True
                if course_flag:
                    if self.__show_names.get():
                        text = c.name
                    else:
                        text = c.number
                    self.agenda.calevent_create(date, text, [tag])
        self.update_selected_dates(None)
        # self.update_tags()
        self.agenda.see(datetime.date(*self.agenda.get_displayed_month()[::-1], 1))

    def show_solutions(self, sol_a, sol_b):
        self.__show_solution(sol_a, EXAMS_A_TAG)
        self.__show_solution(sol_b, EXAMS_B_TAG)
        self.build_display_cp_frame(self.display_cp_frame, sol_a, sol_b)
        self.cp_frame.grid_remove()
        self.display_cp_frame.grid(row=1, column=0, sticky='nsew')

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

        self.agenda.calevent_remove(tag=DATES_INFO_TAG)
        if update_from_selection:
            date_entry.widget.set_date(self.currently_selected_date.get())

        date_a: datetime.date = self.sem_a_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_a_start_entry.label['text'], 'DATES_INFO_TAG')
        while date_a < self.sem_a_a_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['DATES_INFO_TAG', "1st_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_a_a_end_entry.label['text'], 'DATES_INFO_TAG')

        date_a: datetime.date = self.sem_a_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_a_b_start_entry.label['text'], 'DATES_INFO_TAG')
        while date_a < self.sem_a_b_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['DATES_INFO_TAG', "2nd_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_a_b_end_entry.label['text'], 'DATES_INFO_TAG')

        date_a: datetime.date = self.sem_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_b_start_entry.label['text'], 'DATES_INFO_TAG')
        while date_a < self.sem_b_a_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['DATES_INFO_TAG', "1st_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_b_a_end_entry.label['text'], 'DATES_INFO_TAG')

        date_a: datetime.date = self.sem_b_b_start_entry.widget.get_date()
        self.agenda.calevent_create(date_a, self.sem_b_b_start_entry.label['text'], 'DATES_INFO_TAG')
        while date_a < self.sem_b_b_end_entry.widget.get_date():
            self.agenda.calevent_create(date_a, '',
                                        ['DATES_INFO_TAG', "2nd_round"])
            date_a += datetime.timedelta(days=1)
        self.agenda.calevent_create(date_a, self.sem_b_b_end_entry.label['text'], 'DATES_INFO_TAG')

        # self.update_tags()

    def update_tags(self):
        self.agenda.tag_config(MOADEI_A_TAG, background='DodgerBlue2', foreground='red')
        self.agenda.tag_config(EXAMS_A_TAG, background='DodgerBlue2', foreground='red')
        self.agenda.tag_config(MOADEI_B_TAG, background='cyan2', foreground='green')
        self.agenda.tag_config(EXAMS_B_TAG, background='cyan2', foreground='green')
        self.agenda.tag_config(DATES_INFO_TAG, foreground='yellow')
        self.agenda.tag_config(NO_EXAMS_TAG, background='red', foreground='yellow')

    def forbid_date(self, is_forbidden: bool):
        date_to_forbid = self.agenda.selection_get()
        if is_forbidden:
            self.agenda.calevent_create(date_to_forbid, "No Exams", NO_EXAMS_TAG)
            self.__forbidden_dates.append(date_to_forbid)
        else:
            self.agenda.calevent_remove(date=date_to_forbid, tag=NO_EXAMS_TAG)
            self.__forbidden_dates.remove(date_to_forbid)
        self.update_tags()

    def load_files(self):
        # self.__exam_scheduler = ExamScheduler(self.maj_file_input.widget.get_selected_filename(),
        #                                       self.sem_a_courses_file_input.widget.get_selected_filename(),
        #                                       self.sem_b_courses_file_input.widget.get_selected_filename())
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


async def to_thread(func, *args, **kwargs):
    """Asynchronously run function *func* in a separate thread.
    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propogated,
    allowing context variables from the main thread to be accessed in the
    separate thread.
    Return a coroutine that can be awaited to get the eventual result of *func*.
    """
    loop = events.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


if __name__ == '__main__':
    gui = ExamSchedulerGui()
