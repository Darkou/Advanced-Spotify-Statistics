import dotenv
import os
import json

dotenv.load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime
import time

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                            client_secret=client_secret,
                                            redirect_uri=redirect_uri,
                                            scope="user-read-currently-playing"))

def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def getSong():
    last_song = ""
    freeze = False
    freeze_delta = 0
    last_track_ms_played = 0
    while True:
        try: # necessary as if it's the first time, results won't exist yet
            last_track_duration = results["item"]["duration_ms"]
        except:pass
        
        results = sp.current_user_playing_track()  
        
        try:
            if results["is_playing"] == True:
                
                if freeze == True: 
                    unfreeze_time = datetime.datetime.now().timestamp()*1000
                    freeze_delta += int(unfreeze_time - freeze_time)

                if results["item"]["name"] == last_song:
                    
                    if last_track_ms_played <= last_track_duration:
                        last_track_ms_played = int(datetime.datetime.now().timestamp()*1000 - first_play_time - freeze_delta)

                    elif last_track_ms_played > last_track_duration:
                        last_song = ""

                elif results["item"]["name"] != last_song:

                    first_play_time = datetime.datetime.now().timestamp()*1000
                    last_song = results["item"]["name"]

                    track = {}
                    track["ts"] = datetime.datetime.now().isoformat()
                    track["master_metadata_track_name"] = results["item"]["name"]
                    track["master_metadata_album_artist_name"] = results["item"]["artists"][0]["name"]
                    track["master_metadata_album_album_name"] = results["item"]["album"]["name"]
                    track["spotify_track_uri"] = results["item"]["uri"]
                    
                    try: # the file is not empty
                        with open("./history-files/history_99.json", "r+", encoding="utf-8") as fp: # load existant data 
                            data = json.load(fp) # load last track
                            
                            last_track = data[-1] # get the last song written in file
                            del data[-1] # remove the last song in order to replace it with an updated version
                            last_track["ms_played"] = last_track_ms_played # set the played time

                            if last_track_duration - last_track_ms_played > (10/100)*last_track_duration: # consider the song skipped if played no more than 
                                last_track["skipped"] = True
                            else:
                                last_track["skipped"] = False

                            data.append(last_track) # update the last track
                            
                            data.append(track)
                            fp.seek(0)
                            json.dump(data, fp, indent=2)

                    except: # the file is empty
                        data = []
                        with open("./history-files/history_99.json", "w", encoding="utf-8") as fp:
                            data.append(track)
                            json.dump(data, fp, indent=2)

                    last_track_ms_played = 0
                    freeze_delta = 0
                freeze = False
            elif results["is_playing"] == False: # music is paused
                if freeze == False:
                    freeze_time = datetime.datetime.now().timestamp()*1000
                    freeze = True
        
        
        except TypeError: # spotify is not open
            if freeze == False:
                freeze_time = datetime.datetime.now().timestamp()*1000
                freeze = True
        time.sleep(0.5)

if __name__=="__main__":
    getSong()