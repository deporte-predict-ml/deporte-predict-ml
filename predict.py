import os
import requests
import json
from datetime import datetime

# CONFIGURACIÓN DE SEGURIDAD
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
HEADERS = {'X-Auth-Token': API_KEY}

def get_data(url):
    """Extracción con URL corregida y manejo de certificados"""
    try:
        # El dominio correcto debe incluir 'api.'
        # verify=False ayuda si el servidor tiene problemas de certificados
        response = requests.get(url, headers=HEADERS, timeout=20, verify=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al conectar a {url}: {e}")
        return None

def run_predict():
    print(f"--- Iniciando análisis: {datetime.now()} ---")
    predictions = []
    
    # URLS COMPLETAS CON SUBDOMINIO API
    url_standings = "https://football-data.org"
    url_matches = "https://football-data.org"

    print("Conectando a api.football-data.org...")
    standings_data = get_data(url_standings)
    matches_data = get_data(url_matches)

    if standings_data and matches_data:
        team_stats = {}
        try:
            # Extraer puntos
            for table in standings_data.get('standings', []):
                if table['type'] == 'TOTAL':
                    for entry in table['table']:
                        name = entry['team']['name']
                        team_stats[name] = entry['points']
            
            # Analizar próximos 10 partidos
            matches = matches_data.get('matches', [])
            if not matches:
                print("No hay partidos programados próximamente.")
            
            for match in matches[:10]:
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']
                
                h_pts = team_stats.get(home, 0)
                a_pts = team_stats.get(away, 0)
                
                # Lógica: Puntos local vs Visitante
                diff = (h_pts * 1.1) - a_pts
                
                if diff > 7: res = f"Gana {home}"
                elif diff < -7: res = f"Gana {away}"
                else: res = "Empate / Ajustado"

                predictions.append({
                    'partido': f"{home} vs {away}",
                    'prediccion': res,
                    'fecha': match['utcDate']
                })
            print(f"Éxito: {len(predictions)} predicciones generadas.")
        except Exception as e:
            print(f"Error procesando JSON: {e}")

    # Guardar resultados
    output = {
        'status': 'success' if predictions else 'error_no_data',
        'updated_at': datetime.now().isoformat(),
        'data': predictions
    }

    with open('predictions.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("Archivo predictions.json actualizado.")

if __name__ == "__main__":
    if not API_KEY:
        print("ALERTA: No se encontró FOOTBALL_DATA_API_KEY")
    run_predict()
