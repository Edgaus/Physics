from ytmusicapi import YTMusic
import random
import webbrowser
import time
import wikipedia
import re

# Initialize the YouTube Music client
yt = YTMusic()

# Configurar Wikipedia en español (puedes cambiarlo a 'en' si prefieres buscar en inglés)
wikipedia.set_lang("es")

def get_random_game_parameters():
    """
    Returns a randomly selected genre and decade based on weighted probabilities.
    """
    genres = [
        "Rock", "Pop en ingles", "Pop en español", "Banda", 
        "Romantica", "Musica peliculas populares", "Rap/Hip hop", "Baladas"
    ]
    genre_weights = [
        20, 20, 20, # Rock, Pop (English), Pop (Spanish) get higher weights
        8, 8, 8, 8, 8 # The rest get lower, equal weights
    ]
    
    decades = [
        "1920s", "1930s", "1940s", "1950s", "1960s", 
        "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"
    ]
    decade_weights = [
        1, 1, 2, 4, 10, 
        18, 30,         
        16, 10, 5, 3    
    ]
    
    chosen_genre = random.choices(genres, weights=genre_weights, k=1)[0]
    chosen_decade = random.choices(decades, weights=decade_weights, k=1)[0]
    
    return chosen_genre, chosen_decade


def get_real_year_from_wikipedia(title, artist):
    """
    Busca la canción en Wikipedia y usa una expresión regular para encontrar el año.
    """
    # Creamos una búsqueda específica para evitar resultados equivocados
    query = f"{title} {artist} canción"
    
    try:
        # Buscar los resultados más relevantes
        search_results = wikipedia.search(query)
        if not search_results:
            return "No encontrado en Wikipedia"

        # Tomar el primer resultado y obtener un resumen corto (2 oraciones)
        page_title = search_results[0]
        summary = wikipedia.summary(page_title, sentences=2)
        
        # Usar Regex para encontrar un año de 4 dígitos que empiece con 19 o 20
        # (Ejemplo: 1985, 2003)
        year_match = re.search(r'\b(19[2-9]\d|20[0-2]\d)\b', summary)
        
        if year_match:
            return year_match.group(0)
        else:
            return "Año exacto no mencionado en el resumen"

    except wikipedia.exceptions.DisambiguationError as e:
        return "Página de desambiguación (múltiples resultados)"
    except wikipedia.exceptions.PageError:
        return "Página de Wikipedia no encontrada"
    except Exception as e:
        return f"Error en búsqueda: {e}"


def play_random_game_track(category, decade=None):
    """
    category: e.g., 'Rock', 'Pop', 'Jazz'
    decade: e.g., '1990s', '80s' (Optional)
    """
    
    search_query = f"{category} hits"
    if decade:
        search_query = f"{decade} {category} music"
    
    print(f"\n--- 🎲 Game Board Triggered: {search_query} ---")
    
    try:
        results = yt.search(search_query, filter="songs", limit=50)
        
        if not results:
            print("❌ No songs found. Trying a broader search...")
            results = yt.search(category, filter="songs", limit=30)
            if not results:
                return

        random_track = random.choice(results)
        
        title = random_track['title']
        artist = ", ".join([a['name'] for a in random_track['artists']])
        video_id = random_track['videoId']
        url = f"https://music.youtube.com/watch?v={video_id}"

        # --- NUEVA INTEGRACIÓN CON WIKIPEDIA ---
        print("🔍 Buscando el año real de lanzamiento en Wikipedia...")
        real_year = get_real_year_from_wikipedia(title, artist)

        # Display info to the player
        print("\n------------------------------------------")
        print(f"🎵 Now Playing: {title}")
        print(f"🎸 Artist: {artist}")
        print(f"📅 Game Category: {decade} {category}")
        print(f"📖 Real Year (Wikipedia): {real_year}")
        print(f"🔗 Link: {url}")
        print("------------------------------------------\n")

        # Launch the song automatically
        webbrowser.open(url)

    except Exception as e:
        print(f"An error occurred: {e}")

# --- EXAMPLE USAGE FOR YOUR GAME BOARD ---

print("Rolling the dice for a random track...\n")

random_genre, random_decade = get_random_game_parameters()
play_random_game_track(random_genre, random_decade)