from __future__ import annotations

"""
Módulo `core`: lógica reutilizável do projeto (sem GUI e sem CLI).

Objetivo
  - Centralizar a integração com o Open‑Meteo (geocoding + clima atual)
  - Normalizar o JSON retornado em um formato simples (colunas) para CSV
  - Persistir resultados em CSV e TXT (append)
"""

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests


@dataclass(frozen=True)
class Location:
    """
    Estrutura de dados para uma localização resolvida via geocoding.

    Campos
      - name: nome amigável (ex.: "Salvador")
      - latitude/longitude: coordenadas
      - timezone: timezone sugerido pela API (ou "auto")
    """

    name: str
    latitude: float
    longitude: float
    timezone: str


def http_get_json(url: str, params: dict[str, Any], timeout_s: int) -> dict[str, Any]:
    """
    Faz um GET HTTP e retorna o JSON como `dict`.

    Entradas
      - url: endpoint
      - params: querystring
      - timeout_s: timeout de rede em segundos

    Saídas
      - dict com o JSON parseado
    """
    resp = requests.get(url, params=params, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("Resposta inesperada (JSON não-objeto).")
    return data


def geocode_city(city: str, timeout_s: int) -> Location:
    """
    Resolve uma string de cidade para lat/lon/timezone usando o endpoint de geocoding do Open‑Meteo.

    Observação
      - Pedimos apenas o primeiro resultado (`count=1`) para manter o fluxo simples.
    """
    data = http_get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "pt", "format": "json"},
        timeout_s=timeout_s,
    )
    results = data.get("results") or []
    if not results:
        raise ValueError(f"Cidade não encontrada: {city!r}")
    r0 = results[0]
    return Location(
        name=str(r0.get("name") or city),
        latitude=float(r0["latitude"]),
        longitude=float(r0["longitude"]),
        timezone=str(r0.get("timezone") or "auto"),
    )


def fetch_current_weather(lat: float, lon: float, tz: str, timeout_s: int) -> dict[str, Any]:
    """
    Consulta o endpoint de forecast do Open‑Meteo pedindo apenas `current_weather`.

    Saídas
      - O payload retornado é o JSON "cru" da API (dict).
      - A transformação para colunas (CSV) é feita em `flatten_current_weather()`.
    """
    return http_get_json(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "timezone": tz,
            "current_weather": True,
        },
        timeout_s=timeout_s,
    )


def now_utc_isoformat() -> str:
    """
    Retorna o timestamp "agora" em UTC no formato ISO‑8601.

    Exemplo: `2026-04-18T12:00:00+00:00`
    """
    return datetime.now(timezone.utc).isoformat()


def flatten_current_weather(payload: dict[str, Any], collected_at_utc: str, location_name: str) -> dict[str, Any]:
    """
    Converte o JSON da API em um `dict` "achatado" (1 nível), pronto para escrita em CSV.

    Entradas
      - payload: JSON retornado por `fetch_current_weather()`
      - collected_at_utc: quando *nós* coletamos (independente do horário de observação)
      - location_name: nome amigável (cidade) ou fallback "lat,lon"

    Saídas
      - dict com chaves estáveis (colunas)
    """
    cw = payload.get("current_weather") or {}
    return {
        "collected_at_utc": collected_at_utc,
        "location_name": location_name,
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "timezone": payload.get("timezone"),
        "temperature_c": cw.get("temperature"),
        "windspeed_kmh": cw.get("windspeed"),
        "winddirection_deg": cw.get("winddirection"),
        "weathercode": cw.get("weathercode"),
        "is_day": cw.get("is_day"),
        "observed_time_local": cw.get("time"),
    }


def ensure_parent_dir(path: Path) -> None:
    """Garante que o diretório pai exista (ex.: para `out/...`)."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_csv_row(path: Path, row: dict[str, Any]) -> None:
    """
    Adiciona uma linha no CSV (append).

    Efeito colateral
      - Se o arquivo não existe ainda, escreve primeiro o header com as chaves do dict.
    """
    ensure_parent_dir(path)
    headers = list(row.keys())
    file_exists = path.exists()

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def write_notepad_line(path: Path, collected_at_utc: str, location_name: str, temperature_c: Any) -> None:
    """
    Escreve uma linha em TXT no formato:

        YYYY-MM-DD HH:MM:SS,Local,Temperatura

    Observação
      - A data/hora é convertida para UTC‑3 (útil para leitura rápida no Brasil).
    """
    ensure_parent_dir(path)

    try:
        # Usamos o timestamp da coleta (ISO) para manter CSV e TXT coerentes.
        dt_utc = datetime.fromisoformat(collected_at_utc)
    except ValueError:
        # Fallback defensivo: se vier algo inválido, ainda assim escrevemos uma linha.
        dt_utc = datetime.now(timezone.utc)

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    # Por simplicidade, usamos um UTC‑3 fixo (sem regras de horário de verão).
    tz_minus3 = timezone(timedelta(hours=-3))
    dt_minus3 = dt_utc.astimezone(tz_minus3)
    time_str = dt_minus3.strftime("%Y-%m-%d %H:%M:%S")

    temp_str = "" if temperature_c is None else str(temperature_c)
    line = f"{time_str},{location_name},{temp_str}\n"
    with path.open("a", encoding="utf-8", newline="") as f:
        f.write(line)

