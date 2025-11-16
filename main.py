import json
import os
import time
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
try:
    from tkcalendar import DateEntry
except Exception:
    DateEntry = None

AGENDA_FILE = os.path.join(os.path.dirname(__file__), 'agenda.json')


class RelojAgendaApp:
    def __init__(self, root):
        self.root = root
        root.title('Reloj y Agenda - Demo')

        # Simulated datetime and speed
        self.sim_datetime = datetime.now().replace(microsecond=0)
        self.last_real = time.time()
        self.speed = 1.0  # 1x real time

        self.day_count = 0
        self.last_date = self.sim_datetime.date()

        self.agenda = self.load_agenda()

        self.build_ui()
        self.update_clock()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky='nsew')

        # Clock display
        self.clock_label = ttk.Label(frm, text='', font=('Consolas', 32))
        self.clock_label.grid(row=0, column=0, columnspan=3, pady=(0,10))

        self.day_label = ttk.Label(frm, text=f'Días transcurridos: {self.day_count}')
        self.day_label.grid(row=1, column=0, sticky='w')

        # Speed control
        ttk.Label(frm, text='Velocidad:').grid(row=1, column=1, sticky='e')
        self.speed_var = tk.DoubleVar(value=self.speed)
        speed_combo = ttk.Combobox(frm, textvariable=self.speed_var, width=8)
        speed_combo['values'] = (0.1, 1, 10, 60, 3600)
        speed_combo.grid(row=1, column=2, sticky='w')
        speed_combo.bind('<<ComboboxSelected>>', lambda e: self.set_speed())

        # Agenda input
        ttk.Label(frm, text='Nota/Recordatorio:').grid(row=2, column=0, sticky='w')
        self.note_entry = ttk.Entry(frm, width=50)
        self.note_entry.grid(row=2, column=1, columnspan=2, sticky='w')

        ttk.Label(frm, text='Fecha:').grid(row=3, column=0, sticky='w')
        if DateEntry is not None:
            self.date_entry = DateEntry(frm, width=12, year=self.sim_datetime.year,
                                        month=self.sim_datetime.month, day=self.sim_datetime.day,
                                        date_pattern='yyyy-mm-dd')
        else:
            self.date_entry = ttk.Entry(frm, width=15)
            self.date_entry.insert(0, self.sim_datetime.strftime('%Y-%m-%d'))
        self.date_entry.grid(row=3, column=1, sticky='w')

        ttk.Label(frm, text='Hora (HH:MM):').grid(row=3, column=2, sticky='w')
        self.time_entry = ttk.Entry(frm, width=8)
        self.time_entry.insert(0, self.sim_datetime.strftime('%H:%M'))
        self.time_entry.grid(row=3, column=2, sticky='e')

        # Repeat options
        ttk.Label(frm, text='Repetir:').grid(row=4, column=1, sticky='e')
        self.repeat_var = tk.StringVar(value='None')
        repeat_combo = ttk.Combobox(frm, textvariable=self.repeat_var, width=12)
        repeat_combo['values'] = ('None', 'Daily', 'Weekly', 'Monthly', 'Yearly')
        repeat_combo.grid(row=4, column=2, sticky='w')

        add_btn = ttk.Button(frm, text='Añadir a Agenda', command=self.add_note)
        add_btn.grid(row=5, column=0, pady=8)

        del_btn = ttk.Button(frm, text='Eliminar seleccionado', command=self.delete_selected)
        del_btn.grid(row=5, column=1, pady=8)

        complete_btn = ttk.Button(frm, text='Marcar como completado', command=self.mark_completed)
        complete_btn.grid(row=5, column=2, pady=8)

        # Show completed toggle
        self.show_completed = tk.BooleanVar(value=True)
        show_chk = ttk.Checkbutton(frm, text='Mostrar completadas', variable=self.show_completed, command=self.update_listbox)
        show_chk.grid(row=4, column=0, sticky='w')

        # List of reminders
        ttk.Label(frm, text='Agenda / Recordatorios:').grid(row=6, column=0, sticky='w')
        self.listbox = tk.Listbox(frm, width=80, height=10)
        self.listbox.grid(row=7, column=0, columnspan=3, pady=(0,10))
        self.update_listbox()

    def set_speed(self):
        try:
            v = float(self.speed_var.get())
            if v <= 0:
                v = 1.0
        except Exception:
            v = 1.0
        self.speed = v

    def load_agenda(self):
        if os.path.exists(AGENDA_FILE):
            try:
                with open(AGENDA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_agenda(self):
        try:
            with open(AGENDA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.agenda, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print('Error guardando agenda:', e)

    def add_note(self):
        text = self.note_entry.get().strip()
        date_s = self.date_entry.get().strip() if not DateEntry else self.date_entry.get_date().strftime('%Y-%m-%d')
        time_s = self.time_entry.get().strip()
        if not text or not date_s or not time_s:
            messagebox.showwarning('Campos incompletos', 'Complete nota, fecha y hora.')
            return
        try:
            dt = datetime.strptime(f'{date_s} {time_s}', '%Y-%m-%d %H:%M')
        except Exception:
            messagebox.showerror('Formato inválido', 'Fecha u hora con formato incorrecto.')
            return

        note = {
            'id': int(time.time() * 1000),
            'text': text,
            'datetime': dt.isoformat(),
            'triggered': False,
            'repeat': self.repeat_var.get(),
            'completed': False
        }
        self.agenda.append(note)
        self.save_agenda()
        self.update_listbox()
        self.note_entry.delete(0, tk.END)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        note = self.agenda[idx]
        if messagebox.askyesno('Confirmar', f"Eliminar: {note['text']} ?"):
            self.agenda.pop(idx)
            self.save_agenda()
            self.update_listbox()

    def mark_completed(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        note = self.agenda[idx]
        note['completed'] = True
        note['triggered'] = True
        self.save_agenda()
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        try:
            self.agenda.sort(key=lambda n: n['datetime'])
        except Exception:
            pass
        for n in self.agenda:
            if n.get('completed') and not self.show_completed.get():
                continue
            dt = n.get('datetime')
            t = n.get('text')
            status = []
            if n.get('triggered'):
                status.append('activada')
            if n.get('completed'):
                status.append('completada')
            if n.get('repeat') and n.get('repeat') != 'None':
                status.append(f"repite:{n.get('repeat')}")
            stat_s = f" ({', '.join(status)})" if status else ''
            self.listbox.insert(tk.END, f"{dt} - {t}{stat_s}")

    def update_clock(self):
        now_real = time.time()
        elapsed = now_real - self.last_real
        self.last_real = now_real

        # advance simulated datetime by elapsed * speed seconds
        self.sim_datetime += timedelta(seconds=elapsed * self.speed)

        # Check day rollover
        if self.sim_datetime.date() != self.last_date:
            self.day_count += 1
            self.last_date = self.sim_datetime.date()
            self.day_label.config(text=f'Días transcurridos: {self.day_count}')

        # Update clock label
        self.clock_label.config(text=self.sim_datetime.strftime('%Y-%m-%d %H:%M:%S'))

        # Check agenda triggers
        self.check_triggers()

        # schedule next update
        self.root.after(200, self.update_clock)

    def check_triggers(self):
        changed = False
        for n in list(self.agenda):  # copy to allow modification
            if n.get('triggered') and not (n.get('repeat') and n.get('repeat') != 'None'):
                continue
            try:
                note_dt = datetime.fromisoformat(n.get('datetime'))
            except Exception:
                continue
            if self.sim_datetime >= note_dt:
                changed = True
                messagebox.showinfo('Recordatorio', f"{n.get('text')}\nProgramado: {note_dt}")
                rep = n.get('repeat', 'None')
                if rep and rep != 'None':
                    if rep == 'Daily':
                        next_dt = note_dt + timedelta(days=1)
                    elif rep == 'Weekly':
                        next_dt = note_dt + timedelta(weeks=1)
                    elif rep == 'Monthly':
                        next_dt = note_dt + timedelta(days=30)
                    elif rep == 'Yearly':
                        next_dt = note_dt + timedelta(days=365)
                    else:
                        next_dt = note_dt
                    n['datetime'] = next_dt.isoformat()
                    n['triggered'] = False
                else:
                    n['triggered'] = True
        if changed:
            self.save_agenda()
            self.update_listbox()


def main():
    root = tk.Tk()
    app = RelojAgendaApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
