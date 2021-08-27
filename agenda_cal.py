import tkinter

from tkcalendar.calendar_ import *
from tkinter.scrolledtext import ScrolledText

import tkinter as tk


class AgendaLabel(ttk.Label):

    def __init__(self, master=None, **kwargs):
        self.frame = ttk.Frame(master)
        super(AgendaLabel, self).__init__(self.frame, **kwargs)
        self.agenda = ScrolledText(self.frame, height=4, width=20, wrap=tk.WORD, background='gray70', font=(None, 7), state='disabled')

    def configure(self, cnf=None, **kw):
        kkw = dict()
        if 'text' in kw and not kw['text']:
            kkw['text'] = kw['text']
        if 'foreground' in kw:
            kkw['foreground'] = kw['foreground']
        if 'background' in kw:
            kkw['background'] = kw['background']
        super(AgendaLabel, self).configure(cnf, **kw)
        self.agenda.configure(cnf, **kkw)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)
        super(AgendaLabel, self).pack(side='top', expand=True, fill='both')
        self.agenda.pack(side='bottom', expand=True, fill='both')

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)
        super(AgendaLabel, self).pack(side='top', expand=False, fill='x', ipady=1, pady=0)
        self.agenda.pack(side='bottom', expand=True, fill='both')

    def set_agenda_text(self, text: str):
        self.agenda.configure(state=tk.NORMAL)
        self.agenda.delete("1.0", "end")
        self.agenda.insert("end", text, "text")
        self.agenda.tag_config("text", justify=tk.CENTER, font=(None, 7))
        self.agenda.configure(state=tk.DISABLED)

    def bind(self, sequence=None, func=None, add=None):
        super(AgendaLabel, self).bind(sequence, func, add)
        self.agenda.bind(sequence, lambda x: super(AgendaLabel, self).event_generate(sequence, rootx=x.x_root, rooty=x.y_root), add)

    def unbind(self, sequence, funcid=None):
        super(AgendaLabel, self).unbind(sequence, funcid)
        self.agenda.unbind(sequence, funcid)

class Agenda(Calendar):

    def __init__(self, master=None, rightclick_cb=None, **kw):
        curs = kw.pop("cursor", "")
        font = kw.pop("font", "Liberation\ Sans 9")
        classname = kw.pop('class_', "Calendar")
        name = kw.pop('name', None)
        ttk.Frame.__init__(self, master, class_=classname, cursor=curs, name=name)
        self._style_prefixe = str(self)
        ttk.Frame.configure(self, style='main.%s.TFrame' % self._style_prefixe)

        self._textvariable = kw.pop("textvariable", None)

        self._font = Font(self, font)
        prop = self._font.actual()
        prop["size"] += 1
        self._header_font = Font(self, **prop)

        # state
        state = kw.get('state', 'normal')

        try:
            bd = int(kw.pop('borderwidth', 2))
        except ValueError:
            raise ValueError("expected integer for the 'borderwidth' option.")

        firstweekday = kw.pop('firstweekday', 'monday')
        if firstweekday not in ["monday", "sunday"]:
            raise ValueError("'firstweekday' option should be 'monday' or 'sunday'.")
        self._cal = calendar.TextCalendar((firstweekday == 'sunday') * 6)

        weekenddays = kw.pop("weekenddays", None)
        if not weekenddays:
            l = list(self._cal.iterweekdays())
            weekenddays = [l.index(5) + 1, l.index(6) + 1]  # saturday and sunday
        self._check_weekenddays(weekenddays)

        # --- locale
        locale = kw.pop("locale", default_locale())
        if locale is None:
            locale = 'en'
        self._day_names = get_day_names('abbreviated', locale=locale)
        self._month_names = get_month_names('wide', locale=locale)
        date_pattern = self._get_date_pattern(kw.pop("date_pattern", "short"), locale)

        # --- date
        today = self.date.today()

        if self._textvariable is not None:
            # the variable overrides day, month and year keywords
            try:
                self._sel_date = parse_date(self._textvariable.get(), locale)
                month = self._sel_date.month
                year = self._sel_date.year
            except IndexError:
                self._sel_date = None
                self._textvariable.set('')
                month = kw.pop("month", today.month)
                year = kw.pop('year', today.year)
        else:
            if (("month" in kw) or ("year" in kw)) and ("day" not in kw):
                month = kw.pop("month", today.month)
                year = kw.pop('year', today.year)
                self._sel_date = None  # selected day
            else:
                day = kw.pop('day', today.day)
                month = kw.pop("month", today.month)
                year = kw.pop('year', today.year)
                try:
                    self._sel_date = self.date(year, month, day)  # selected day
                except ValueError:
                    self._sel_date = None

        self._date = self.date(year, month, 1)  # (year, month) displayed by the calendar

        # --- date limits
        maxdate = kw.pop('maxdate', None)
        mindate = kw.pop('mindate', None)
        if maxdate is not None:
            if isinstance(maxdate, self.datetime):
                maxdate = maxdate.date()
            elif not isinstance(maxdate, self.date):
                raise TypeError("expected %s for the 'maxdate' option." % self.date)
        if mindate is not None:
            if isinstance(mindate, self.datetime):
                mindate = mindate.date()
            elif not isinstance(mindate, self.date):
                raise TypeError("expected %s for the 'mindate' option." % self.date)
        if (mindate is not None) and (maxdate is not None) and (mindate > maxdate):
            raise ValueError("mindate should be smaller than maxdate.")

        # --- selectmode
        selectmode = kw.pop("selectmode", "day")
        if selectmode not in ("none", "day"):
            raise ValueError("'selectmode' option should be 'none' or 'day'.")
        # --- show week numbers
        showweeknumbers = kw.pop('showweeknumbers', True)

        # --- style
        self.style = ttk.Style(self)
        active_bg = self.style.lookup('TEntry', 'selectbackground', ('focus',))
        dis_active_bg = self.style.lookup('TEntry', 'selectbackground', ('disabled',))
        dis_bg = self.style.lookup('TLabel', 'background', ('disabled',))
        dis_fg = self.style.lookup('TLabel', 'foreground', ('disabled',))

        # --- properties
        options = ['cursor',
                   'font',
                   'borderwidth',
                   'state',
                   'selectmode',
                   'textvariable',
                   'locale',
                   'date_pattern',
                   'maxdate',
                   'mindate',
                   'showweeknumbers',
                   'showothermonthdays',
                   'firstweekday',
                   'weekenddays',
                   'selectbackground',
                   'selectforeground',
                   'disabledselectbackground',
                   'disabledselectforeground',
                   'normalbackground',
                   'normalforeground',
                   'background',
                   'foreground',
                   'disabledbackground',
                   'disabledforeground',
                   'bordercolor',
                   'othermonthforeground',
                   'othermonthbackground',
                   'othermonthweforeground',
                   'othermonthwebackground',
                   'weekendbackground',
                   'weekendforeground',
                   'headersbackground',
                   'headersforeground',
                   'disableddaybackground',
                   'disableddayforeground',
                   'tooltipforeground',
                   'tooltipbackground',
                   'tooltipalpha',
                   'tooltipdelay']

        keys = list(kw.keys())
        for option in keys:
            if option not in options:
                del (kw[option])

        self._properties = {"cursor": curs,
                            "font": font,
                            "borderwidth": bd,
                            "state": state,
                            "locale": locale,
                            "date_pattern": date_pattern,
                            "selectmode": selectmode,
                            'textvariable': self._textvariable,
                            'firstweekday': firstweekday,
                            'weekenddays': weekenddays,
                            'mindate': mindate,
                            'maxdate': maxdate,
                            'showweeknumbers': showweeknumbers,
                            'showothermonthdays': kw.pop('showothermonthdays', True),
                            'selectbackground': active_bg,
                            'selectforeground': 'white',
                            'disabledselectbackground': dis_active_bg,
                            'disabledselectforeground': 'white',
                            'normalbackground': 'white',
                            'normalforeground': 'black',
                            'background': 'gray30',
                            'foreground': 'white',
                            'disabledbackground': 'gray30',
                            'disabledforeground': 'gray70',
                            'bordercolor': 'gray70',
                            'othermonthforeground': 'gray45',
                            'othermonthbackground': 'gray93',
                            'othermonthweforeground': 'gray45',
                            'othermonthwebackground': 'gray75',
                            'weekendbackground': 'gray80',
                            'weekendforeground': 'gray30',
                            'headersbackground': 'gray70',
                            'headersforeground': 'black',
                            'disableddaybackground': dis_bg,
                            'disableddayforeground': dis_fg,
                            'tooltipforeground': 'gray90',
                            'tooltipbackground': 'black',
                            'tooltipalpha': 0.8,
                            'tooltipdelay': 2000}
        self._properties.update(kw)

        # --- calevents
        self.calevents = {}  # special events displayed in colors and with tooltips to show content
        self._calevent_dates = {}  # list of event ids for each date
        self._tags = {}  # tags to format event display
        self.tooltip_wrapper = TooltipWrapper(self,
                                              alpha=self._properties['tooltipalpha'],
                                              style=self._style_prefixe + '.tooltip.TLabel',
                                              delay=self._properties['tooltipdelay'])

        # --- init calendar
        # --- *-- header: month - year
        self._header = ttk.Frame(self, style='main.%s.TFrame' % self._style_prefixe)

        f_month = ttk.Frame(self._header,
                            style='main.%s.TFrame' % self._style_prefixe)
        self._l_month = ttk.Button(f_month,
                                   style='L.%s.TButton' % self._style_prefixe,
                                   command=self._prev_month)
        self._header_month = ttk.Label(f_month, width=10, anchor='center',
                                       style='main.%s.TLabel' % self._style_prefixe, font=self._header_font)
        self._r_month = ttk.Button(f_month,
                                   style='R.%s.TButton' % self._style_prefixe,
                                   command=self._next_month)
        self._l_month.pack(side='left', fill="y")
        self._header_month.pack(side='left', padx=4)
        self._r_month.pack(side='left', fill="y")

        f_year = ttk.Frame(self._header, style='main.%s.TFrame' % self._style_prefixe)
        self._l_year = ttk.Button(f_year, style='L.%s.TButton' % self._style_prefixe,
                                  command=self._prev_year)
        self._header_year = ttk.Label(f_year, width=4, anchor='center',
                                      style='main.%s.TLabel' % self._style_prefixe, font=self._header_font)
        self._r_year = ttk.Button(f_year, style='R.%s.TButton' % self._style_prefixe,
                                  command=self._next_year)
        self._l_year.pack(side='left', fill="y")
        self._header_year.pack(side='left', padx=4)
        self._r_year.pack(side='left', fill="y")

        f_month.pack(side='left', fill='x')
        f_year.pack(side='right')

        # --- *-- calendar
        self._cal_frame = ttk.Frame(self,
                                    style='cal.%s.TFrame' % self._style_prefixe)

        ttk.Label(self._cal_frame,
                  style='headers.%s.TLabel' % self._style_prefixe).grid(row=0,
                                                                        column=0,
                                                                        sticky="eswn")
        # week day names
        self._week_days = []
        for i, day in enumerate(self._cal.iterweekdays()):
            d = self._day_names[day % 7]
            self._cal_frame.columnconfigure(i + 1, weight=1)
            self._week_days.append(ttk.Label(self._cal_frame,
                                             font=self._font,
                                             style='headers.%s.TLabel' % self._style_prefixe,
                                             anchor="center",
                                             text=d, width=4))
            self._week_days[-1].grid(row=0, column=i + 1, sticky="ew", pady=(0, 1))
        self._week_nbs = []  # week numbers
        self._calendar = []  # days
        for i in range(1, 7):
            self._cal_frame.rowconfigure(i, weight=1)
            wlabel = ttk.Label(self._cal_frame, style='headers.%s.TLabel' % self._style_prefixe,
                               font=self._font, padding=2,
                               anchor="e", width=2)
            self._week_nbs.append(wlabel)
            wlabel.grid(row=i, column=0, sticky="esnw", padx=(0, 1))
            if not showweeknumbers:
                wlabel.grid_remove()
            self._calendar.append([])
            for j in range(1, 8):
                label = AgendaLabel(self._cal_frame, style='normal.%s.TLabel' % self._style_prefixe,
                                    font=self._font, anchor="center")
                self._calendar[-1].append(label)
                label.grid(row=i, column=j, padx=(0, 1), pady=(0, 1), sticky="nsew")
                if selectmode == "day":
                    label.bind("<1>", self._on_click)

        # --- *-- pack main elements
        self._header.pack(fill="x", padx=2, pady=2)
        self._cal_frame.pack(fill="both", expand=True, padx=bd, pady=bd)

        self.config(state=state)

        # --- bindings
        self.bind('<<ThemeChanged>>', self._setup_style)

        self._setup_style()
        self._display_calendar()
        self._btns_date_range()
        self._check_sel_date()

        if self._textvariable is not None:
            try:
                self._textvariable_trace_id = self._textvariable.trace_add('write', self._textvariable_trace)
            except AttributeError:
                self._textvariable_trace_id = self._textvariable.trace('w', self._textvariable_trace)

        self.__right_click_callback = rightclick_cb
        # change a bit the options of the labels to improve display
        for i, row in enumerate(self._calendar):
            for j, label in enumerate(row):
                self._cal_frame.rowconfigure(i + 1, uniform=1, minsize=100)
                self._cal_frame.columnconfigure(j + 1, uniform=1, minsize=100)
                # label.configure(justify="center", anchor="n", padding=(1, 4))
                label.bind("<Button-3>", lambda event: self.__on_rightclick(event))
                label.grid_propagate(0)

    def __on_rightclick(self, event):
        event.widget.event_generate("<Button-1>")
        self.after_idle(lambda: self.__right_click_callback(event))

    def set_rightclick_callback(self, cb):
        self.__right_click_callback = cb

    def _display_days_without_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdays2calendar(year, month)
        while len(cal) < 6:
            cal.append([(0, i) for i in range(7)])

        week_days = {i: 'normal.%s.TLabel' % self._style_prefixe for i in
                     range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we.%s.TLabel' % self._style_prefixe
        week_days[self['weekenddays'][1] - 1] = 'we.%s.TLabel' % self._style_prefixe
        _, week_nb, d = self._date.isocalendar()
        if d == 7 and self['firstweekday'] == 'sunday':
            week_nb += 1
        modulo = max(week_nb, 52)
        for i_week in range(6):
            if i_week == 0 or cal[i_week][0][0]:
                self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            else:
                self._week_nbs[i_week].configure(text='')
            for i_day in range(7):
                day_number, week_day = cal[i_week][i_day]
                style = week_days[i_day]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                if day_number:
                    txt = str(day_number)
                    label.configure(text=txt, style=style)
                    label.set_agenda_text('')
                    date = self.date(year, month, day_number)
                    if date in self._calevent_dates:
                        ev_ids = self._calevent_dates[date]
                        i = len(ev_ids) - 1
                        while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                            i -= 1
                        if i >= 0:
                            tag = self.calevents[ev_ids[i]]['tags'][-1]
                            label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                        # modified lines:
                        text = '%s' % day_number
                        label.configure(text=text)
                        label.set_agenda_text('\n'.join([self.calevents[ev]['text'] for ev in ev_ids]))
                else:
                    label.configure(text='', style=style)

    def _display_days_with_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdatescalendar(year, month)

        next_m = month + 1
        y = year
        if next_m == 13:
            next_m = 1
            y += 1
        if len(cal) < 6:
            if cal[-1][-1].month == month:
                i = 0
            else:
                i = 1
            cal.append(self._cal.monthdatescalendar(y, next_m)[i])
            if len(cal) < 6:
                cal.append(self._cal.monthdatescalendar(y, next_m)[i + 1])

        week_days = {i: 'normal' for i in range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we'
        week_days[self['weekenddays'][1] - 1] = 'we'
        prev_m = (month - 2) % 12 + 1
        months = {month: '.%s.TLabel' % self._style_prefixe,
                  next_m: '_om.%s.TLabel' % self._style_prefixe,
                  prev_m: '_om.%s.TLabel' % self._style_prefixe}

        week_nb = cal[0][1].isocalendar()[1]
        modulo = max(week_nb, 52)
        for i_week in range(6):
            self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            for i_day in range(7):
                style = week_days[i_day] + months[cal[i_week][i_day].month]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                txt = str(cal[i_week][i_day].day)
                label.configure(text=txt, style=style)
                label.set_agenda_text('')
                if cal[i_week][i_day] in self._calevent_dates:
                    date = cal[i_week][i_day]
                    ev_ids = self._calevent_dates[date]
                    i = len(ev_ids) - 1
                    while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                        i -= 1
                    if i >= 0:
                        tag = self.calevents[ev_ids[i]]['tags'][-1]
                        label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                    # modified lines:
                    text = '%s' % date.day
                    label.configure(text=text)
                    label.set_agenda_text('\n'.join([self.calevents[ev]['text'] for ev in ev_ids]))

    def _show_event(self, date):
        """Display events on date if visible."""
        w, d = self._get_day_coords(date)
        if w is not None:
            label = self._calendar[w][d]
            if not label.cget('text'):
                # this is an other month's day and showothermonth is False
                return
            ev_ids = self._calevent_dates[date]
            i = len(ev_ids) - 1
            while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                i -= 1
            if i >= 0:
                tag = self.calevents[ev_ids[i]]['tags'][-1]
                label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
            # modified lines:
            text = '%s' % date.day
            label.configure(text=text)
            label.set_agenda_text('\n'.join([self.calevents[ev]['text'] for ev in ev_ids]))

        # --- bindings

    def _on_click(self, event):
        """Select the day on which the user clicked."""
        if self._properties['state'] == 'normal':
            label = event.widget
            if "disabled" not in label.state():
                day = label.cget("text")
                style = label.cget("style")
                # if style in ['normal_om.%s.TLabel' % self._style_prefixe,
                #              'we_om.%s.TLabel' % self._style_prefixe]:
                if int(day) > 7 and label in self._calendar[0]:
                    self._prev_month()
                elif (int(day) < 5 and label in self._calendar[-2]) or (int(day) < 12 and label in self._calendar[-1]):
                    self._next_month()
                if day:
                    day = int(day)
                    year, month = self._date.year, self._date.month
                    self._remove_selection()
                    self._sel_date = self.date(year, month, day)
                    self._display_selection()
                    if self._textvariable is not None:
                        self._textvariable.set(self.format_date(self._sel_date))
                    self.event_generate("<<CalendarSelected>>")

if __name__ == '__main__':
    import tkinter as tk

    root = tk.Tk()
    root.geometry("800x500")
    agenda = Agenda(root, selectmode='none')
    date = agenda.datetime.today() + agenda.timedelta(days=2)
    agenda.calevent_create(date, 'Hello World', 'message')
    agenda.calevent_create(date, 'Reminder 2', 'reminder')
    agenda.calevent_create(date + agenda.timedelta(days=-7), 'Reminder 1', 'reminder')
    agenda.calevent_create(date + agenda.timedelta(days=3), 'Message', 'message')
    agenda.calevent_create(date + agenda.timedelta(days=3), 'Another message', 'message')

    agenda.tag_config('reminder', background='red', foreground='yellow')

    agenda.pack(fill="both", expand=True)
    root.mainloop()
