import os
import requests
import json
from datetime import datetime

# CONFIGURACIÓN
# Aseguramos la barra final para evitar el error ConnectionError anterior
BASE_URL = "https://football-data.org"
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
HEADERS = {'X-Auth-Token': API_KEY}

def get_data(endpoint):
    """Obtiene datos de la API manejando la URL correctamente."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # Lanza error si la respuesta no es 200
        return response.json()
    except Exception as e:
        print(f"Error al conectar con {url}: {e}")
        return None

def run_predict():
    print(f"--- Iniciando Sistema Cuantitativo: {datetime.now()} ---")

    # 1. Obtener clasificación de La Liga (PD = Primera División)
    standings_data = get_data("competitions/PD/standings")
    if not standings_data:
        return

    # Crear mapa de puntos por equipo
    team_stats = {}
    for table in standings_data.get('standings', []):
        if table['type'] == 'TOTAL':
            for entry in table['table']:
                team_name = entry['team']['name']
                team_stats[team_name] = {
                    'points': entry['points'],
                    'goalsFor': entry['goalsFor'],
                    'position': entry['position']
                }

    # 2. Obtener próximos partidos
    matches_data = get_data("competitions/PD/matches?status=SCHEDULED")
    if not matches_data:
        return

    predictions = []
    
    # 3. Lógica de Predicción
    # Analizamos los próximos 10 partidos programados
    for match in matches_data.get('matches', [])[:10]:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        match_date = match['utcDate']

        # Obtener métricas de cada equipo
        home_info = team_stats.get(home_team, {'points': 0})
        away_info = team_stats.get(away_team, {'points': 0})

        # Cálculo de fuerza: Puntos + un pequeño bono por localía (15%)
        home_power = home_info['points'] * 1.15
        away_power = away_info['points']

        # Determinar resultado
        diff = home_power - away_power
        
        if diff > 10:
            pred = f"Victoria clara: {home_team}"
            conf = "Alta"
        elif diff > 3:
            pred = f"Favorito: {home_team}"
            conf = "Media"
        elif diff < -10:
            pred = f"Victoria clara: {away_team}"
            conf = "Alta"
        elif diff < -3:
            pred = f"Favorito: {away_team}"
            conf = "Media"
        else:
            pred = "Empate muy probable / Partido cerrado"
            conf = "Baja"

        predictions.append({
            'partido': f"{home_team} vs {away_team}",
            'fecha': match_date,
            'prediccion': pred,
            'confianza': conf,
            'metrica_dif': round(diff, 2)
        })

    # 4. Guardar resultados en JSON
    output = {
        'actualizado_el': datetime.now().isoformat(),
        'total_analizados': len(predictions),
        'resultados': predictions
    }

    with open('predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print("Archivo predictions.json generado con éxito.")

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: La variable FOOTBALL_DATA_API_KEY no está configurada.")
    else:
        run_predict()
