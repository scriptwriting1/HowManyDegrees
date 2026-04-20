from __future__ import annotations

"""
Módulo `gui`: interface gráfica (Tkinter) do projeto.

Objetivo
  - Permitir que o usuário digite uma cidade e consulte o clima atual
  - Persistir os resultados em CSV/TXT (append) para histórico simples
"""

from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk

from .core import (
    fetch_current_weather,
    flatten_current_weather,
    geocode_city,
    now_utc_isoformat,
    write_csv_row,
    write_notepad_line,
)
from .weather_codes import describe_weathercode_pt


class WeatherApp:
    def __init__(self, root: tk.Tk, output_dir: Path):
        self.root = root
        self.root.title("Consulta do Clima")
        self.root.geometry("400x300")
        self.root.resizable(True, True)

        # Diretório onde os outputs serão gravados (padrão: <raiz do projeto>/out).
        self.output_dir = output_dir
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.create_widgets()

    def create_widgets(self) -> None:
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        title_label = ttk.Label(main_frame, text="Consulta do Clima", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(main_frame, text="Cidade:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.city_var = tk.StringVar()
        self.city_entry = ttk.Entry(main_frame, textvariable=self.city_var, width=30, font=("Helvetica", 10))
        self.city_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.city_entry.focus()
        self.city_entry.bind("<Return>", lambda _e: self.search_weather())

        self.search_btn = ttk.Button(main_frame, text="Buscar Clima", command=self.search_weather)
        self.search_btn.grid(row=2, column=0, columnspan=2, pady=20)

        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=200)
        self.progress.grid(row=3, column=0, columnspan=2, pady=10)
        self.progress.grid_remove()

        results_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        self.results_text = tk.Text(
            results_frame,
            height=8,
            width=40,
            wrap=tk.WORD,
            font=("Courier", 9),
            state="disabled",
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        results_frame.rowconfigure(0, weight=1)

        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para consultar o clima")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def search_weather(self) -> None:
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Entrada Inválida", "Por favor, digite o nome de uma cidade.")
            return

        # Travamos a UI e exibimos um progressbar enquanto a consulta é feita.
        self.search_btn.config(state="disabled")
        self.city_entry.config(state="disabled")
        self.progress.grid()
        self.progress.start(10)
        self.status_var.set(f"Buscando clima para {city}...")
        self.clear_results()

        # Agendamos a execução para logo após o loop do Tkinter "respirar".
        # (Para um app maior, aqui seria o ponto para usar threads.)
        self.root.after(100, lambda: self.perform_search(city))

    def perform_search(self, city: str) -> None:
        try:
            # 1) Cidade -> coordenadas + timezone (geocoding)
            loc = geocode_city(city, timeout_s=20)
            # 2) Coordenadas -> current_weather
            payload = fetch_current_weather(loc.latitude, loc.longitude, loc.timezone, timeout_s=20)

            collected_at_utc = now_utc_isoformat()
            # 3) Payload "cru" -> dict com colunas amigáveis (para CSV)
            row = flatten_current_weather(payload, collected_at_utc=collected_at_utc, location_name=loc.name)

            csv_path = self.output_dir / "weather.csv"
            txt_path = self.output_dir / "weather.txt"

            # 4) Persistência: cada busca adiciona 1 linha (append) nos arquivos.
            write_csv_row(csv_path, row)
            write_notepad_line(
                txt_path,
                collected_at_utc=collected_at_utc,
                location_name=loc.name,
                temperature_c=row.get("temperature_c"),
            )

            self.display_results(row, loc.name)
            # Mostramos o caminho absoluto para o usuário não "perder" onde foi salvo.
            self.status_var.set(f"Salvo em: {csv_path.resolve()} e {txt_path.resolve()}")
        except ValueError as e:
            if "Cidade não encontrada" in str(e):
                messagebox.showerror("Cidade Não Encontrada", f"Não foi possível encontrar a cidade: {city}")
                self.status_var.set("Cidade não encontrada")
            else:
                messagebox.showerror("Erro de Validação", str(e))
                self.status_var.set("Erro de validação")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao buscar o clima:\n{str(e)}")
            self.status_var.set("Erro na consulta")
        finally:
            self.progress.stop()
            self.progress.grid_remove()
            self.search_btn.config(state="normal")
            self.city_entry.config(state="normal")
            self.city_entry.focus()

    def display_results(self, row: dict, location_name: str) -> None:
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)

        # Extraímos as colunas do dict para formatar a apresentação ao usuário.
        temp = row.get("temperature_c")
        windspeed = row.get("windspeed_kmh")
        winddir = row.get("winddirection_deg")
        weathercode = row.get("weathercode")
        is_day = row.get("is_day")
        observed_time = row.get("observed_time_local")

        # Traduzimos o "weathercode" num texto amigável (pt‑BR).
        desc = describe_weathercode_pt(weathercode if weathercode is None else int(weathercode))
        day_night = "Dia" if is_day == 1 else "Noite" if is_day == 0 else "Desconhecido"

        result_text = f"""Local: {location_name}
Temperatura: {temp}°C
Velocidade do vento: {windspeed} km/h
Direção do vento: {winddir}°
Condição: {desc}
Período: {day_night}
Horário local da observação: {observed_time}
"""

        self.results_text.insert(tk.END, result_text)
        self.results_text.config(state="disabled")

    def clear_results(self) -> None:
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")


def main(project_root: Path | None = None) -> None:
    """
    Entrypoint da GUI.

    Entradas
      - project_root: quando fornecido, fixa onde os outputs serão gravados.

    Observação
      - Isso é importante quando a GUI é executada por atalhos/IDE, onde o "cwd" pode variar.
    """
    root = tk.Tk()
    resolved_root = project_root or Path.cwd()
    _app = WeatherApp(root, output_dir=resolved_root / "out")
    root.mainloop()

