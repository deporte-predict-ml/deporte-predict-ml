import os
import requests
import json
from datetime import datetime

def run_predict():
    print(f"--- Iniciando análisis: {datetime.now()} ---")
    api_key = os.getenv('FOOTBALL_DATA_API_KEY')
    headers = {'X-Auth-Token': api_key}
    predictions = []
    
    # URLS FORZADAS DENTRO DEL CÓDIGO
    url_standings = "https://football-data.org"
    url_matches = "https://football-data.org"

    print("Intentando conectar a api.football-data.org...")
    
    try:
        # 1. Obtener Clasificación
        r_standings = requests.get(url_standings, headers=headers, timeout=20)
        r_standings.raise_for_status()
        standings_data = r_standings.json()

        # 2. Obtener Partidos
        r_matches = requests.get(url_matches, headers=headers, timeout=20)
        r_matches.raise_for_status()
        matches_data = r_matches.json()

        # 3. Procesar Datos
        team_stats = {}
        for table in standings_data.get('standings', []):
            if table['type'] == 'TOTAL':
                for entry in table['table']:
                    team_stats[entry['team']['name']] = entry['points']

        for match in matches_data.get('matches', [])[:10]:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            h_pts = team_stats.get(home, 0)
            a_pts = team_stats.get(away, 0)
            
            diff = (h_pts * 1.1) - a_pts
            res = "Gana " + home if diff > 7 else ("Gana " + away if diff < -7 else "Empate")

            predictions.append({
                'partido': f"{home} vs {away}",
                'prediccion': res,
                'fecha': match['utcDate']
            })
        print(f"Éxito: {len(predictions)} predicciones.")

    except Exception as e:
        print(f"ERROR DEFINITIVO: {e}")

    # Guardar siempre el archivo
    output = {
        'status': 'ok' if predictions else 'error',
        'updated_at': datetime.now().isoformat(),
        'data': predictions
    }

    with open('predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("Archivo predictions.json guardado.")

if __name__ == "__main__":
    run_predict()
