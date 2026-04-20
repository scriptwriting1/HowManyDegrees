from __future__ import annotations

"""
Módulo `cli`: interface de linha de comando do projeto.

Objetivo
  - Ler parâmetros (cidade OU lat/lon)
  - Consultar Open‑Meteo (via `howmanydegrees.core`)
  - Persistir o resultado em CSV + TXT (append)
"""

import argparse
import sys
from pathlib import Path

import requests

from .core import (
    fetch_current_weather,
    flatten_current_weather,
    geocode_city,
    now_utc_isoformat,
    write_csv_row,
    write_notepad_line,
)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Consulta clima (Open-Meteo) e salva uma linha em CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # O usuário escolhe um dos dois modos: cidade (geocoding) OU coordenadas (lat/lon).
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--city", help="Nome da cidade (ex: 'São Paulo').")
    group.add_argument("--lat", type=float, help="Latitude (se não usar --city).")
    p.add_argument("--lon", type=float, help="Longitude (obrigatório se usar --lat).")
    p.add_argument("--timezone", default="auto", help="Timezone para a resposta (ex: 'America/Sao_Paulo' ou 'auto').")
    p.add_argument("--out", default="out/weather.csv", help="Caminho do CSV de saída.")
    p.add_argument("--notepad", default="out/weather.txt", help="Caminho do TXT para 'horario UTC-3,local,temperatura'.")
    p.add_argument("--timeout", type=int, default=20, help="Timeout HTTP (segundos).")
    return p


def main(argv: list[str]) -> int:
    args = build_arg_parser().parse_args(argv)
    out_path = Path(args.out)
    notepad_path = Path(args.notepad)

    if args.city:
        # 1) Cidade -> coordenadas (geocoding)
        loc = geocode_city(args.city, timeout_s=args.timeout)
        # "auto" usa o timezone retornado pelo geocoding.
        tz = args.timezone if args.timezone != "auto" else loc.timezone
        lat, lon = loc.latitude, loc.longitude
        location_name = loc.name
    else:
        if args.lon is None:
            raise SystemExit("Você usou --lat, então precisa informar também --lon.")
        # 2) Coordenadas fornecidas direto pelo usuário (sem geocoding)
        lat, lon = float(args.lat), float(args.lon)
        tz = args.timezone
        location_name = f"{lat},{lon}"

    # Timestamp da coleta (UTC) para auditoria e para ordenar no CSV.
    collected_at_utc = now_utc_isoformat()
    # Consulta o "current_weather" do Open‑Meteo e transforma em colunas.
    payload = fetch_current_weather(lat, lon, tz, timeout_s=args.timeout)
    row = flatten_current_weather(payload, collected_at_utc=collected_at_utc, location_name=location_name)
    # Persistência (append): cada execução adiciona 1 linha nos arquivos.
    write_csv_row(out_path, row)
    write_notepad_line(
        notepad_path,
        collected_at_utc=collected_at_utc,
        location_name=location_name,
        temperature_c=row.get("temperature_c"),
    )

    print(f"OK: gravou 1 linha em {out_path.resolve()} e {notepad_path.resolve()}")
    return 0


def run() -> None:
    """
    Entrypoint do CLI.

    Usado tanto pelo wrapper da raiz (`weather_to_csv.py`) quanto por eventuais execuções via módulo.
    """
    try:
        raise SystemExit(main(sys.argv[1:]))
    except requests.HTTPError as e:
        # Erros HTTP (4xx/5xx) retornados pela API.
        print(f"Erro HTTP: {e}", file=sys.stderr)
        raise
    except requests.RequestException as e:
        # Problemas de rede/DNS/timeout etc.
        print(f"Erro de rede: {e}", file=sys.stderr)
        raise

