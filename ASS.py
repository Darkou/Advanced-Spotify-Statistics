#darkou :)

import json 
import glob
import re
import calendar
import datetime, time

import modules.pystyle as pystyle
from modules.pystyle import Colors, Colorate, Center
from colorama import Fore, Style

pystyle.System.Title("Advanced Spotify Statistics (ASS)")
print(Colors.white, "")
pystyle.System.Clear()

history_files = sorted(glob.glob("./history-files/*.json"), key=lambda item: item[-6]) #make list of all files (sorted from oldest to most recent)
history = []
for file in history_files: 
    with open(file, 'r', encoding="utf8") as f:
        history += json.load(f) #make list of all song dicts (sorted from oldest to most recent)

start_date = re.split(r":|-| |T", history[0]["ts"])[0:3] # set data start date in list [year, month, day]
end_date = re.split(r":|-| |T", history[-1]["ts"])[0:3] # set data end date in list [year, month, day]

def Page():
    display_date_window = f"Data from {start_date[2]} {list(calendar.month_name)[int(start_date[1])]} {(start_date[0])} to {end_date[2]} {list(calendar.month_name)[int(end_date[1])]} {(end_date[0])}."

    print(pystyle.Box.Lines("\nAdvanced Spotify Statistics (ASS)\n"))
    print(Center.XCenter(display_date_window))
    print("\n")

def Where():
    r = input(f"{Fore.GREEN}[1] All time\n[2] Year\n[3] Month \n[4] Week \n> {Style.RESET_ALL}")

    try:
        r = int(r)
    except:
        pystyle.System.Clear()
        Page()
        Where()
    
    if r == 1:
        Stats(time.time(), "ALL-TIME") # all time
    elif r == 2:
        Stats(31556926, "YEAR") # 1 year in epoch
    elif r == 3:
        Stats(2629743, "MONTH") # 1 month in epoch
    elif r == 4:
        Stats(604800, "WEEK") # 1 week in epoch
    else:pass

def Stats(range, type):
    pystyle.System.Clear()

    total_time = 0
    total_streams = 0
    total_unique_tracks = {}
    total_artists = {}
    first_time = False

    for song in history:
        song_name = song["master_metadata_track_name"]
        song_artist = song["master_metadata_album_artist_name"]
        song_played_time = song["ms_played"]
        
        song_date = re.split(r":|-| |T", song["ts"]) # set song date in list [year, month, day, hour, min, s]  
        song_date[-1] = song_date[-1][0:2] # delete junk from second
        song_date = [int(i) for i in song_date] # convert to int each el
        song_date = datetime.datetime(song_date[0], song_date[1], song_date[2], song_date[3], song_date[4], song_date[5]).timestamp()

        if song_date >= int(time.time())-range:
            if not first_time: 
                first_date = re.split(r":|-| |T", song["ts"])[0:3] # set song date but only year, month, day
                first_date_full = re.split(r":|-| |T", song["ts"]) # set song date in list [year, month, day, hour, min, s]
                first_date_full[-1] = first_date_full[-1][0:2] # delete junk from second
                first_date_full = [int(i) for i in first_date_full] # convert to int each el
                first_date_epoch = datetime.datetime(first_date_full[0], first_date_full[1], first_date_full[2], first_date_full[3], first_date_full[4], first_date_full[5]).timestamp()
                first_time = True

            total_streams += 1
            total_time += song_played_time
        
            if song_name not in total_unique_tracks: 
                total_unique_tracks[song_name] = [1, song_played_time]
            else:
                total_unique_tracks[song_name][0] = int(total_unique_tracks[song_name][0]) + 1
                total_unique_tracks[song_name][1] = int(total_unique_tracks[song_name][1]) + song_played_time

            if song_artist not in total_artists:
                total_artists[song_artist] = [1, song_played_time]
            else:
                total_artists[song_artist][0] = int(total_artists[song_artist][0]) + 1
                total_artists[song_artist][1] = int(total_artists[song_artist][1]) + song_played_time
    
    last_date = re.split(r":|-| |T", song["ts"])[0:3] # set song date but only year, month, day
    last_date_full = re.split(r":|-| |T", song["ts"]) # set song date in list [year, month, day, hour, min, s]
    last_date_full[-1] = last_date_full[-1][0:2] # delete junk from second
    last_date_full = [int(i) for i in last_date_full] # convert to int each el
    last_date_epoch = datetime.datetime(last_date_full[0], last_date_full[1], last_date_full[2], last_date_full[3], last_date_full[4], last_date_full[5]).timestamp()

    #set up for display
    total_time = total_time/1000 # convert ms to s

    min, s = divmod(total_time, 60)
    h, min = divmod(min, 60)
    d, h = divmod(h, 24)
    d, h, min, s = int(d), int(h), int(min), int(s)

    #sort dict by streamed time
    total_unique_tracks = dict(sorted(total_unique_tracks.items(), reverse=True, key=lambda item: item[1][1])) 
    total_artists = dict(sorted(total_artists.items(), reverse=True, key=lambda item: item[1][1]))

    #display init
    try:
        display_date_window = f"Data from {first_date[2]} {list(calendar.month_name)[int(first_date[1])]} {(first_date[0])} to {last_date[2]} {list(calendar.month_name)[int(last_date[1])]} {(last_date[0])}."
        display_total_time = f"Total time streamed  :" + f"\n> {(d*24+h)*60+min} minutes \n> {d*24+h} hours \n> {d} days, {h} hours, {min} minutes, {s} seconds. "
        display_average_time = f"Average daily time : {int(((d*24+h)*60+min)/((last_date_epoch-first_date_epoch)/86400))} minutes/day"
        display_total_streams = f"Total streams : {total_streams}"
        display_total_unique_tracks = f"Total unique tracks : {len(total_unique_tracks)} ({int(len(total_unique_tracks)/total_streams*100)}%)"
        display_total_artists = f"Total artists : {len(total_artists)}"
        display_top_tracks = "Top tracks :"
        display_top_artists = "Top artists :"
    except UnboundLocalError:
        print(Colorate.Color(Colors.red, "There is not enough data to display that."))
        time.sleep(3)
        pystyle.System.Clear()
        Page()
        Where()
    except Exception as e:
        print(Colorate.Color(Colors.red, f"An error may have occured. ({e})"))
        time.sleep(3)
        pystyle.System.Clear()
        Page()
        Where()

    #display print
    print(pystyle.Box.Lines("\n"+type+" STATISTICS"+"\n"))
    print(Center.XCenter(display_date_window))
    print("\n")
    print(pystyle.Box.DoubleCube(display_total_time))
    print(pystyle.Box.DoubleCube(display_average_time))
    print(pystyle.Box.DoubleCube(display_total_streams))
    print(pystyle.Box.DoubleCube(display_total_unique_tracks))
    print(pystyle.Box.DoubleCube(display_total_artists))

    # TOP TRACKS
    i=0
    while i < 10:
        track_name = list(total_unique_tracks.keys())[i]
        if i+1 == 10: 
            display_top_tracks += f"\n#{i+1} - {track_name} " +f"({int(total_unique_tracks[track_name][1]/1000//60)} minutes)"
        else:
            display_top_tracks += f"\n#{i+1}  - {track_name} " + f"({int(total_unique_tracks[track_name][1]/1000//60)} minutes)"
        i += 1
    print(pystyle.Box.DoubleCube(display_top_tracks))

    # TOP ARTISTS
    i=0
    while i < 10:
        artist_name = list(total_artists.keys())[i]
        if i+1 == 10: 
            display_top_artists += f"\n#{i+1} - {artist_name} " + f"({int(total_artists[artist_name][1]/1000//60)} minutes)"
        else:
            display_top_artists += f"\n#{i+1}  - {artist_name} " + f"({int(total_artists[artist_name][1]/1000//60)} minutes)"
        i += 1
    print(pystyle.Box.DoubleCube(display_top_artists))

    Where()

if __name__ == "__main__":
    Page()
    Where()