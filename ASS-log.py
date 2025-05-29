# darkou :)

from pystyle import *
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

def log():
    # variables initialization
    last_song = ""
    paused = False
    pause_delta = 0
    last_track_ms_played = 0
    file_number = 100
    file_year = datetime.datetime.now().year

    while True: # catch all kinds of error, especially with the api
        try:
            try: # necessary because if it's the first time, results won't exist yet
                last_track_duration = results["item"]["duration_ms"]
            except:pass
            
            results = sp.current_user_playing_track() # get currently playing track to json format
            
            try:
                if results["is_playing"] == True:
                    
                    if paused == True: # meaning that it's just after music is unpaused so we can calculate the pause time
                        unpause_time = datetime.datetime.now().timestamp()*1000
                        pause_delta += int(unpause_time - pause_time)

                    if results["item"]["name"] == last_song:
                        
                        if last_track_ms_played <= last_track_duration:
                            last_track_ms_played = int(datetime.datetime.now().timestamp()*1000 - first_play_time - pause_delta)

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
                            with open(f"./history-files/ass_log_streaming_history_{file_year}_{file_number}.json", "r+", encoding="utf-8") as fp: # load existant data 
                                data = json.load(fp) # load last track
                                
                                try: # skip that part if that's the first song
                                    last_track = data[-1] # get the last song written in file
                                    del data[-1] # remove the last song in order to replace it with an updated version
                                    last_track["ms_played"] = last_track_ms_played # set the played time

                                    if last_track_duration - last_track_ms_played > (10/100)*last_track_duration: # consider the song skipped if played less than 90%
                                        last_track["skipped"] = True
                                    else:
                                        last_track["skipped"] = False

                                    data.append(last_track) # update the last track
                                except:pass

                                data.append(track) # add new track
                                fp.seek(0)
                                json.dump(data, fp, indent=2)

                        except Exception as e: # the file is empty
                            data = []
                            with open(f"./history-files/ass_log_streaming_history_{file_year}_{file_number}.json", "a", encoding="utf-8") as fp:
                                data.append(track)
                                json.dump(data, fp, indent=2)

                        last_track_ms_played = 0
                        pause_delta = 0
                    paused = False

                elif results["is_playing"] == False: # music is paused
                    if paused == False:
                        pause_time = datetime.datetime.now().timestamp()*1000
                        paused = True
                    
                    if os.path.getsize(f"./history-files/ass_log_streaming_history_{file_year}_{file_number}.json") > 12000000:
                        file_number += 1
                        file_year = datetime.datetime.now().year

            
            except TypeError: # spotify is not open
                if paused == False:
                    pause_time = datetime.datetime.now().timestamp()*1000
                    paused = True
                
                if os.path.getsize(f"./history-files/ass_log_streaming_history_{file_year}_{file_number}.json") > 12000000:
                    file_number += 1
                    file_year = datetime.datetime.now().year
            
            time.sleep(0.5) # requests will be done every x seconds

        except Exception as e:
            print(e) # in case there is an error with the api, we just ignore it

if __name__=="__main__":
    log()