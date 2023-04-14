from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

SPOTIPY_CLIENT_ID = os.getenv("spotipy_client_id")
SPOTIPY_CLIENT_SECRET = os.getenv("spotipy_client_secret")
SPOTIPY_REDIRECT_URI = "http://example.com/callback/"


# Scraping Billboard 100
date = input("Which year do you want to travel to? Type the data in this format YYYY-MM-DD: ")
URL = "https://www.billboard.com/charts/hot-100/"+date+"/"

response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
song_list = soup.select("li ul li h3")
song_names = [song.get_text().strip() for song in song_list]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=SPOTIPY_REDIRECT_URI,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# Searching Spotify for songs by title
song_URIs = []
for song in song_names:
    res = sp.search(q=f"track:{song} year:{date[:4]}", type="track")
    try:
        uri = res["tracks"]["items"][0]["uri"]
        song_URIs.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped")

# Creating a new private playlist in spotify
new_playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
new_playlist_id = new_playlist["id"]

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=new_playlist_id, items=song_URIs)




