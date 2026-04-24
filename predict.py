import os
import requests
import pandas as pd
import json
from datetime import datetime

# Configuración de acceso
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = "https://football-data.org"
HEADERS = {'X-Auth-Token': API_KEY}

def get_data(endpoint):
    response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener datos: {response.status_code}")
        return None

def simple_predict():
    print("Iniciando análisis de predicciones...")
    
    # 1. Obtener la clasificación de La Liga (PD = Primera División)
    standings = get_data("competitions/PD/standings")
    if not standings: return

    # Crear un diccionario de fortaleza de equipo basado en su posición
    # A menor posición (1º), mayor es el 'score'
    team_strength = {}
    for team in standings['standings'][0]['table']:
        team_name = team['team']['name']
        points = team['points']
        team_strength[team_name] = points

    # 2. Obtener los próximos partidos
    scheduled_matches = get_data("competitions/PD/matches?status=SCHEDULED")
    if not scheduled_matches: return

    predictions = []

    # 3. Lógica Cuantitativa Básica (Modelo de Puntos)
    for match in scheduled_matches['matches'][:10]:  # Analizar los próximos 10
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        home_score = team_strength.get(home_team, 0)
        away_score = team_strength.get(away_score, 0)
        
        # Factor campo: +10% de ventaja al local
        home_score *= 1.10

        if home_score > away_score * 1.05:
            result = f"Gana {home_team}"
            prob = "Alta"
        elif away_score > home_score * 1.05:
            result = f"Gana {away_team}"
            prob = "Alta"
        else:
            result = "Empate / Muy ajustado"
            prob = "Media"

        predictions.append({
            'fecha': match['utcDate'],
            'partido': f"{home_team} vs {away_team}",
            'prediccion': result,
            'confianza': prob
        })

    # 4. Guardar resultados
    output = {
        'ultima_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'predicciones': predictions
    }
    
    with open('predictions.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print("Predicciones guardadas en predictions.json")

if __name__ == "__main__":
    if not API_KEY:
        print("Error: No se encontró la API KEY en los Secrets de GitHub.")
    else:
        simple_predict()
