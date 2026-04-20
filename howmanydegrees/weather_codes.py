from __future__ import annotations

WEATHER_DESCRIPTIONS_PT: dict[int, str] = {
    0: "Céu limpo",
    1: "Principalmente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com depositação de gelo",
    51: "Garagem leve",
    53: "Garagem moderada",
    55: "Garagem densa",
    56: "Garagem congelante leve",
    57: "Garagem congelante densa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    66: "Chuva congelante leve",
    67: "Chuva congelante forte",
    71: "Queda de neve leve",
    73: "Queda de neve moderada",
    75: "Queda de neve forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva leves",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva violentas",
    85: "Pancadas de neve leves",
    86: "Pancadas de neve fortes",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte",
}


def describe_weathercode_pt(weathercode: int | None) -> str:
    if weathercode is None:
        return "Código desconhecido"
    return WEATHER_DESCRIPTIONS_PT.get(int(weathercode), f"Código {weathercode}")

