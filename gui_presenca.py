import pandas as pd
from datetime import datetime
import os
import re
import tkinter as tk
from tkinter import ttk

SHEET_ID = '1RX6L8yxukcRhLoih3gH6BUsrx4JgZeIG4duKSu8ciIU'
URL_HORARIOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1651859946"
URLS_TASKS = {
    "Bancada Mono": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=766295141",
    "Bancada VW": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=146544989",
    "Bloco Motores": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0",
    "Trocador Calor": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=790239595"
}

def get_tasks_from_sheets():
    tasks = {}
    for proj, url in URLS_TASKS.items():
        try:
            df = pd.read_csv(url, header=None, dtype=str).fillna("")
            for _, row in df.iterrows():
                if len(row) < 5: continue
                task = str(row.iloc[2]).strip()
                resp = str(row.iloc[4]).strip()
                finished = str(row.iloc[9]).strip() if len(row) > 9 else ""
                
                if task and resp and resp.lower() != "responsavel" and task.lower() != "descrição da tarefa" and len(task) > 1:
                    if finished.lower() == "ok":
                            continue
                            
                    for name in [n.strip() for n in resp.split(',')]:
                        if name and len(name) > 1:
                            if name not in tasks: tasks[name] = []
                            if not any(t["task"] == task for t in tasks[name]):
                                tasks[name].append({"project": proj, "task": task})
        except Exception as e:
            pass # Silently fail
    return tasks

class PresenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Presença")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")
        
        # Estilos modernos
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), background="#f0f2f5")
        style.configure("Time.TLabel", font=("Helvetica", 12), background="#f0f2f5")
        style.configure("Header.TLabel", font=("Helvetica", 11, "bold"), background="#f0f2f5", foreground="#5f6368")
        style.configure("CurrentHeader.TLabel", font=("Helvetica", 13, "bold"), background="#f0f2f5", foreground="#1a73e8")

        # Container Principal
        self.main_frame = tk.Frame(root, bg="#f0f2f5", padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        self.lbl_title = ttk.Label(self.main_frame, text="Monitor de Presença", style="Title.TLabel")
        self.lbl_title.pack(pady=(0, 5))

        self.lbl_time = ttk.Label(self.main_frame, text="Carregando...", style="Time.TLabel")
        self.lbl_time.pack(pady=(0, 20))

        # Grid para as 3 colunas (Passada, Atual, Próxima)
        self.columns_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        self.columns_frame.pack(expand=True, fill="both")
        self.columns_frame.columnconfigure(0, weight=1)
        self.columns_frame.columnconfigure(1, weight=1)
        self.columns_frame.columnconfigure(2, weight=1)

        # --- Coluna Hora Passada ---
        self.frame_past = tk.Frame(self.columns_frame, bg="#f0f2f5", padx=10)
        self.frame_past.grid(row=0, column=0, sticky="nsew")
        self.lbl_header_past = ttk.Label(self.frame_past, text="HORA PASSADA", style="Header.TLabel")
        self.lbl_header_past.pack(pady=5)
        self.list_past = self.create_listbox(self.frame_past)

        # --- Coluna Hora Atual ---
        self.frame_now = tk.Frame(self.columns_frame, bg="#f0f2f5", padx=10)
        self.frame_now.grid(row=0, column=1, sticky="nsew")
        self.lbl_header_now = ttk.Label(self.frame_now, text="AGORA", style="CurrentHeader.TLabel")
        self.lbl_header_now.pack(pady=5)
        self.list_now = self.create_listbox(self.frame_now, highlight="#1a73e8")

        # --- Coluna Hora Seguinte ---
        self.frame_next = tk.Frame(self.columns_frame, bg="#f0f2f5", padx=10)
        self.frame_next.grid(row=0, column=2, sticky="nsew")
        self.lbl_header_next = ttk.Label(self.frame_next, text="PRÓXIMA HORA", style="Header.TLabel")
        self.lbl_header_next.pack(pady=5)
        self.list_next = self.create_listbox(self.frame_next)

        self.lbl_status = ttk.Label(self.main_frame, text="Iniciando...", font=("Helvetica", 9), background="#f0f2f5", foreground="#70757a")
        self.lbl_status.pack(pady=(15, 0))

        # Iniciar o update_presence no after
        self.update_presence()

    def create_listbox(self, parent, highlight="#dcdfe6"):
        frame = tk.Frame(parent, bg="white", highlightbackground=highlight, highlightthickness=2)
        frame.pack(expand=True, fill="both")
        
        lb = tk.Listbox(
            frame, 
            font=("Helvetica", 11), 
            borderwidth=0, 
            highlightthickness=0,
            selectmode=tk.NONE,
            bg="white",
            fg="#3c4043"
        )
        lb.pack(side="left", expand=True, fill="both", padx=2, pady=2)
        
        sb = ttk.Scrollbar(frame, orient="vertical", command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.config(yscrollcommand=sb.set)
        return lb

    def get_people_for_hour(self, df, weekday, hour_to_check):
        days_map = {0: (1, 9), 1: (9, 17), 2: (17, 25), 3: (25, 33), 4: (33, 40)}
        
        if weekday > 4:
            return ["Fim de semana"]

        target_row = None
        for i, row in df.iterrows():
            time_str = str(row[0]).strip()
            parts = re.findall(r'\d+', time_str)
            if len(parts) >= 2:
                try:
                    if ":" not in time_str:
                        start_h, end_h = int(parts[0]), int(parts[1])
                        if start_h <= hour_to_check < end_h:
                            target_row = row
                            break
                    else:
                        time_parts = re.split(r'[–-]', time_str)
                        if len(time_parts) == 2:
                            check_time = datetime.strptime(f"{hour_to_check:02d}:01", '%H:%M').time()
                            start_t = datetime.strptime(time_parts[0].strip(), '%H:%M').time()
                            end_t = datetime.strptime(time_parts[1].strip(), '%H:%M').time()
                            if start_t <= check_time < end_t:
                                target_row = row
                                break
                except: continue
        
        if target_row is None:
            return ["-"]

        col_start, col_end = days_map[weekday]
        present = []
        for val in target_row.iloc[col_start:col_end]:
            if pd.notna(val) and str(val).strip() != "" and str(val).lower() != "nan" and str(val).lower() != "horas":
                present.append(str(val).strip())
        
        return sorted(list(set(present))) if present else ["Ninguém"]

    def update_presence(self):
        day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        now = datetime.now()
        weekday = now.weekday()
        current_hour = now.hour
        
        self.lbl_time.config(text=f"{now.strftime('%H:%M')} - {day_names[weekday]}")

        self.lbl_header_past.config(text=f"{(current_hour-1)%24:02d}:00 - {current_hour:02d}:00")
        self.lbl_header_now.config(text=f"AGORA ({current_hour:02d}:00 - {(current_hour+1)%24:02d}:00)")
        self.lbl_header_next.config(text=f"{(current_hour+1)%24:02d}:00 - {(current_hour+2)%24:02d}:00")

        self.lbl_status.config(text="Sincronizando com o Google Sheets (Versão GitHub)...")
        self.root.update()

        try:
            # Baixa o CSV diretamente
            df = pd.read_csv(URL_HORARIOS, header=None)
            tasks_map = get_tasks_from_sheets()
            
            # Coleta dados
            past_people = self.get_people_for_hour(df, weekday, (current_hour - 1) % 24)
            now_people = self.get_people_for_hour(df, weekday, current_hour)
            next_people = self.get_people_for_hour(df, weekday, (current_hour + 1) % 24)

            # Popula listboxes
            for lb, people in zip([self.list_past, self.list_now, self.list_next], [past_people, now_people, next_people]):
                lb.delete(0, tk.END)
                for p in people:
                    lb.insert(tk.END, f"  • {p}")
                    if p in tasks_map:
                        for t in tasks_map[p]:
                            task_desc = t['task'].replace(chr(10), ' ')
                            lb.insert(tk.END, f"      [{t['project']}] {task_desc}")
                        lb.insert(tk.END, "") # blank line

            self.lbl_status.config(text=f"Próxima mudança de escala às {(now.hour + 1) % 24:02d}:00")

        except Exception as e:
            for lb in [self.list_past, self.list_now, self.list_next]:
                lb.delete(0, tk.END)
            self.list_now.insert(tk.END, f"Erro ao acessar Google Sheets:")
            self.list_now.insert(tk.END, f"{str(e)}")
            self.lbl_status.config(text="Erro de sincronização.")
        
        self.root.after(60000, self.update_presence)

if __name__ == "__main__":
    root = tk.Tk()
    app = PresenceApp(root)
    root.mainloop()

