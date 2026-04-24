import os
import requests
import json
from datetime import datetime

BASE_URL = "https://football-data.org"
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
HEADERS = {'X-Auth-Token': API_KEY}

def get_data(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error en API: {e}")
        return None

def run_predict():
    print("Iniciando análisis...")
    predictions = []
    
    # Intentar obtener datos
    standings_data = get_data("competitions/PD/standings")
    matches_data = get_data("competitions/PD/matches?status=SCHEDULED")

    if standings_data and matches_data:
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
            
            # Algoritmo simple de fuerza
            diff = (h_pts * 1.1) - a_pts
            
            if diff > 8: res = f"Gana {home}"
            elif diff < -8: res = f"Gana {away}"
            else: res = "Posible Empate"

            predictions.append({
                'partido': f"{home} vs {away}",
                'prediccion': res,
                'fecha': match['utcDate']
            })

    # SIEMPRE generamos el archivo, aunque sea con error o vacío
    # Esto evita que el comando 'git add' del YAML falle
    output = {
        'status': 'success' if predictions else 'no_data_or_error',
        'updated_at': datetime.now().isoformat(),
        'data': predictions
    }

    with open('predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("Proceso finalizado. Archivo guardado.")

if __name__ == "__main__":
    run_predict()
