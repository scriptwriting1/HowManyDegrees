# Weather → CSV (Open‑Meteo)

Script em Python que consulta uma API de clima e salva o resultado em um CSV (1 linha por execução).

O projeto é organizado como um pequeno pacote (`howmanydegrees/`) com **entrypoints legados** na raiz
(`weather_to_csv.py` e `weather_gui.py`) para manter compatibilidade com os comandos abaixo.

## Instalação

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

### Por cidade (geocoding automático)

```bash
python weather_to_csv.py --city "São Paulo"
```

### Por latitude/longitude

```bash
python weather_to_csv.py --lat -23.5505 --lon -46.6333 --timezone "America/Sao_Paulo"
```

### GUI (Tkinter)

```bash
python weather_gui.py
```

## Saída (CSV)

Por padrão, os arquivos são gravados em `out/weather.csv` e `out/weather.txt`.

### Observação sobre `out/` (dados de exemplo)

Este repositório já inclui `out/weather.csv` e `out/weather.txt` com **dados de teste/exemplo** de propósito,
para quem estiver visualizando poder entender rapidamente o formato da saída sem precisar rodar nada.

Quando você rodar o programa, ele **não sobrescreve** os arquivos: ele faz **append** (adiciona novas linhas no final).
Assim dá para comparar claramente:

- o que já estava no repositório (meus testes/exemplos)
- o que foi gerado por você ao executar o script/GUI

Se preferir gerar apenas seus próprios registros, basta **remover as linhas de teste/exemplo** desses arquivos antes de executar.

Mais detalhes em `out/README.md`.

O CSV terá colunas como:

- `collected_at_utc`
- `location_name`
- `latitude`, `longitude`, `timezone`
- `temperature_c`, `windspeed_kmh`, `winddirection_deg`
- `weathercode`, `is_day`, `observed_time_local`

API usada: Open‑Meteo (sem chave).
