import os
import requests
import json
from datetime import datetime

# URLS FORZADAS PARA EVITAR ERRORES DE UNIÓN
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
HEADERS = {'X-Auth-Token': API_KEY}

def get_data(url):
    """Función de extracción con URL directa"""
    try:
        # Forzamos el timeout y los headers
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error crítico en API al conectar a {url}: {e}")
        return None

def run_predict():
    print(f"--- Iniciando análisis: {datetime.now()} ---")
    predictions = []
    
    # URLS COMPLETAS Y DIRECTAS
    url_standings = "https://football-data.org"
    url_matches = "https://football-data.org"

    print("Obteniendo clasificación...")
    standings_data = get_data(url_standings)
    
    print("Obteniendo próximos partidos...")
    matches_data = get_data(url_matches)

    if standings_data and matches_data:
        team_stats = {}
        # Extraer puntos de la tabla
        try:
            for table in standings_data.get('standings', []):
                if table['type'] == 'TOTAL':
                    for entry in table['table']:
                        team_stats[entry['team']['name']] = entry['points']
            
            # Analizar partidos
            for match in matches_data.get('matches', [])[:10]:
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']
                
                h_pts = team_stats.get(home, 0)
                a_pts = team_stats.get(away, 0)
                
                # Algoritmo de fuerza: Puntos local (con 10% bono) vs Puntos visitante
                diff = (h_pts * 1.1) - a_pts
                
                if diff > 7: res = f"Gana {home}"
                elif diff < -7: res = f"Gana {away}"
                else: res = "Empate / Muy ajustado"

                predictions.append({
                    'partido': f"{home} vs {away}",
                    'prediccion': res,
                    'fecha': match['utcDate']
                })
            print(f"Se procesaron {len(predictions)} predicciones.")
        except Exception as e:
            print(f"Error procesando los datos: {e}")

    # Guardar siempre para que GitHub Actions no falle
    output = {
        'status': 'success' if predictions else 'error_de_datos',
        'updated_at': datetime.now().isoformat(),
        'data': predictions
    }

    with open('predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("Archivo predictions.json guardado correctamente.")

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: No se detectó la API KEY en los Secrets de GitHub.")
    run_predict()
