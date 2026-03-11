import pandas as pd
from datetime import datetime
import os
import re

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
                            if name not in tasks:
                                tasks[name] = []
                            # Previne duplicatas
                            if not any(t["task"] == task for t in tasks[name]):
                                tasks[name].append({"project": proj, "task": task})
        except Exception as e:
            print(f"Erro ao obter tarefas de {proj}: {e}")
    return tasks

def get_present_people():
    try:
        # Carrega a planilha a partir do Google Sheets (versão do github)
        df = pd.read_csv(URL_HORARIOS, header=None)
        
        # Mapeamento de dias
        days_map = {
            0: (1, 9),   # Segunda
            1: (9, 17),  # Terça
            2: (17, 25), # Quarta
            3: (25, 33), # Quinta
            4: (33, 40)  # Sexta
        }
        
        day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        
        now = datetime.now()
        weekday = now.weekday()
        hour = now.hour
        
        print(f"Horário atual: {now.strftime('%H:%M')} ({day_names[weekday]})")
        
        if weekday > 4:
            print("Hoje é final de semana. Não há ninguém listado para hoje.")
            return

        target_row = None
        for i, row in df.iterrows():
            time_str = str(row[0]).strip()
            parts = re.findall(r'\d+', time_str)
            
            if len(parts) >= 2:
                try:
                    if ":" in time_str:
                        time_parts = re.split(r'[–-]', time_str)
                        if len(time_parts) == 2:
                            start_time = datetime.strptime(time_parts[0].strip(), '%H:%M').time()
                            end_time = datetime.strptime(time_parts[1].strip(), '%H:%M').time()
                            current_time = now.time()
                            if start_time <= current_time < end_time:
                                target_row = row
                                break
                    else:
                        start_h = int(parts[0])
                        end_h = int(parts[1])
                        if start_h <= hour < end_h:
                            target_row = row
                            break
                except:
                    continue
            
            if target_row is None and time_str.startswith(str(hour) + " "):
                target_row = row
                break
        
        if target_row is None:
            print(f"Não foi encontrado um intervalo para a hora {hour}:00 na planilha.")
            return

        col_start, col_end = days_map[weekday]
        
        present = []
        for val in target_row.iloc[col_start:col_end]:
            if pd.notna(val) and str(val).strip() != "" and str(val).lower() != "nan" and str(val).lower() != "horas":
                present.append(str(val).strip())
        
        if present:
            tasks_map = get_tasks_from_sheets()
            print("\nPessoas presentes agora:")
            for p in sorted(list(set(present))):
                print(f"\n- {p}")
                if p in tasks_map:
                    for t in tasks_map[p]:
                        print(f"  [{t['project']}] {t['task'].replace(chr(10), ' ')}")
        else:
            print("\nNinguém está listado como presente neste horário.")

    except Exception as e:
        print(f"Erro ao processar a planilha: {e}")

if __name__ == "__main__":
    get_present_people()
