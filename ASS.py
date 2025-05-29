# darkou :)

import json
import glob

import calendar
import datetime
import os
import time
import dotenv
from tqdm import tqdm

from tkinter import Tk, filedialog

from pystyle import *
from colorama import Fore, Style

System.Title("Advanced Spotify Statistics")
System.Clear()

Tk().withdraw()

dotenv.load_dotenv()

local_path = os.getenv("LOCAL_PATH")
smb_path = os.getenv("SMB_PATH")

history_files = []
smb_history_files = []

has_smb = False

if local_path==None:
    print(f"{Fore.RED}Select the folder that contains your .json Extended Streaming History files from Spotify. \nSelecting the root folder will automatically look for a default folder 'history-files'.")

    local_path = filedialog.askdirectory(initialdir=os.path.abspath(os.getcwd()),
                                            title='Please select a directory')

    System.Clear()

    if local_path==os.path.abspath(os.getcwd()).replace("\\", "/") or local_path=="":
        local_path="./history-files/*.json"
    else:
        local_path+="/*.json"

    with open(".env", "a", encoding="utf-8") as f:
        f.write("\n\nLOCAL_PATH="+'"'+local_path+'"')

if smb_path==None:
    has_smb = input(f"{Fore.RED}Do you want to select a folder located on a remote server (through SMB) ? (Y/N=any){Style.RESET_ALL}\n>").lower().strip()

    if has_smb=="y" or has_smb=="yes":
        has_smb = True
        print("On your remote server (through SMB protocol), select the folder that contains your .json files created by ASS-log.py.")
        smb_path = filedialog.askdirectory(initialdir=os.path.abspath(os.getcwd()),
                                                title='Please select a directory')
        with open(".env", "a", encoding="utf-8") as f:
            f.write("\nSMB_PATH="+'"'+smb_path+'"')
    else:
        with open(".env", "a", encoding="utf-8") as f:
            f.write('\nSMB_PATH=""')
        System.Clear()
        pass
elif smb_path=="": #so that it won't ask for smb path next time
    pass
else:
    has_smb = True

System.Clear()

print(f"{Fore.GREEN}\nCrawling through your file(s)... Please wait...{Style.RESET_ALL}\n")

history_local = []

history_files = sorted(glob.glob(local_path), key=lambda file: int(file[file.rindex("_")+1:file.rindex(".")])) # make list of all files (sorted from oldest to most recent)

for file in tqdm(history_files): 
    with open(file, 'r', encoding="utf8") as f:
        history_local += json.load(f) # make list of all song dicts (sorted from oldest to most recent)

last_date_local = datetime.datetime.fromisoformat((history_local[-1]["ts"])).timestamp()

if has_smb:
    smb_history_files = sorted(glob.glob(smb_path+"/*.json"), key=lambda file: int(file[file.rindex("_")+1:file.rindex(".")])) # make list of all files (sorted from oldest to most recent)

    history_smb = []

    for file in tqdm(smb_history_files): 
        with open(file, 'r', encoding="utf8") as f:
            history_smb += json.load(f) # make list of all song dicts (sorted from oldest to most recent)

    for idx, track_smb in enumerate(history_smb):
        print(idx)
        if datetime.datetime.fromisoformat(track_smb["ts"]).timestamp() < last_date_local:
            print(datetime.datetime.fromisoformat(track_smb["ts"]).timestamp())
            del history_smb[idx]
        else:
            break
    history = history_local + history_smb
else:
    history = history_local

try:
    start_date = datetime.datetime.fromisoformat(history[0]["ts"]).timetuple() # set data start date from iso to tuple
    start_datetime = datetime.datetime.fromisoformat(history[0]["ts"])
    end_date = datetime.datetime.fromisoformat(history[-1]["ts"]).timetuple() # set data end date from iso to tuple
except:
    print(f"{Fore.RED}\tThere was a problem with the selected file(s). (exiting...){Style.RESET_ALL}")
    quit()

def Page():
    display_date_window = f"Data from {start_date[2]} {list(calendar.month_name)[int(start_date[1])]} {(start_date[0])} to {end_date[2]} {list(calendar.month_name)[int(end_date[1])]} {(end_date[0])}."

    print(Box.Lines("\nAdvanced Spotify Statistics (ASS)\n"))
    print(Center.XCenter(display_date_window))
    print("\n")

def Where():
    r = input(f"{Fore.GREEN}\n\n\n[1] All time\n[2] Year\n[3] Month \n[4] Week \n[5] Today \n[6] Custom \n> {Style.RESET_ALL}")

    try:
        r = int(r[0])
    except:
        System.Clear()
        Page()
        Where()
    
    dt = datetime.datetime.now()
    dt_ts = dt.timestamp()

    print(dt.year)

    if r == 1:
        Stats(time.time(), "ALL-TIME") # all time
    elif r == 2:
        dt = datetime.datetime(dt.year, 1, 2, 0, 0).timestamp()
        Stats(dt_ts-dt, "YEAR") # 1 year in epoch
    elif r == 3:
        dt = datetime.datetime(dt.year, dt.month, 2, 0, 0).timestamp()
        Stats(dt_ts-dt, "MONTH") # 1 month in epoch
    elif r == 4:
        dt = datetime.datetime(dt.year, dt.month, dt.day-6, 0, 0).timestamp()
        Stats(dt_ts-dt, "WEEK") # 1 week in epoch
    elif r == 5:
        dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0).timestamp()
        Stats(dt_ts-dt, "TODAY") # 1 week in epoch
    elif r == 6:
        keywords = ["day", "days", "week", "weeks", "month", "months", "year", "years"]

        def getTimestamp(operator, indice): # convert indice to timestamp
            custom_time = 0
            if indice == "day" or indice == "days":
                custom_time = operator*86400
            elif indice == "week" or indice == "weeks":
                custom_time = operator*604800 
            elif indice == "month" or indice == "months":
                custom_time = operator*2629743 
            elif indice == "year" or indice == "years":
                custom_time = operator*31556926
            return custom_time

        def getTime(type):
            answer = input(f"{Fore.CYAN}\n\t"+"{preposition} ".format(preposition="From" if type=="FROM" else "To") + f"{Fore.BLUE}(dd-mm-yyyy or keywords) {Fore.CYAN}> {Style.RESET_ALL}")
            error = False
            if "-" in answer:
                try:
                    answer = [int(i) for i in answer.split("-")] 
                    return int(time.time()-datetime.datetime(answer[2], answer[1], answer[0]).timestamp()) # don't know why int() but it works
                except:
                    print(f"{Fore.RED}\tFormat not accepted.{Style.RESET_ALL}")
                    return None
            else:
                for index, word in enumerate(answer.split()):
                    if word in keywords:
                        try:
                            operator = int(answer.split()[index-1])
                            return getTimestamp(operator, str(word)) 
                        except ValueError:
                            error = True
                    elif word == "today":
                        return 0
                    else:
                        error = True

                if error:
                    print(f"{Fore.RED}\tFormat not accepted.{Style.RESET_ALL}")
                    return None
                # return maximum when no input
                else:
                    if type == "FROM":
                        return time.time()
                    elif type == "TO":
                        return 0

        from_time = getTime("FROM")
        isDone = False
        while isDone is not True:
            if from_time == None:
                from_time = getTime("FROM")
            else:
                isDone = True

        to_time = getTime("TO")
        isDone = False
        while isDone is not True:
            if to_time == None:
                to_time = getTime("TO")
            else:
                isDone = True

        print(from_time, to_time)

        if from_time <= to_time:
            print(f"{Fore.RED}\tEnd date cannot be before start date.{Style.RESET_ALL}")
            from_time = getTime("FROM")
            to_time = getTime("TO")
        else:
            Stats(from_time, "CUSTOM", to_time) 

    else:
        System.Clear()
        Page()
        Where()

def Stats(from_time, type, to_time=0):
    System.Clear()

    total_time = 0
    total_streams = 0
    total_unique_tracks = {}
    total_artists = {}
    total_albums = {}

    first = True

    for song in history:
        try:
            song_name = song["master_metadata_track_name"]
            song_artist = song["master_metadata_album_artist_name"]
            song_album = song["master_metadata_album_album_name"]
            song_played_time = song["ms_played"]
            song_date = datetime.datetime.fromisoformat(song["ts"])

            if int(time.time())-to_time >= int(datetime.datetime.timestamp(song_date)) >= int(time.time())-from_time:
                if first: # get variables of first date taken into account
                    first_date_epoch = datetime.datetime.timestamp(song_date)
                    first_date = song_date.timetuple()
                    first = False

                total_streams += 1
                total_time += song_played_time
            
                if song_name not in total_unique_tracks: 
                    total_unique_tracks[song_name] = [1, song_played_time, song_artist]
                else:
                    total_unique_tracks[song_name][0] = int(total_unique_tracks[song_name][0]) + 1
                    total_unique_tracks[song_name][1] = int(total_unique_tracks[song_name][1]) + song_played_time

                if song_artist not in total_artists:
                    total_artists[song_artist] = [1, song_played_time]
                else:
                    total_artists[song_artist][0] = int(total_artists[song_artist][0]) + 1
                    total_artists[song_artist][1] = int(total_artists[song_artist][1]) + song_played_time

                if song_album not in total_albums:
                    total_albums[song_album] = [1, song_played_time, song_artist]
                else:
                    total_albums[song_album][0] = int(total_albums[song_album][0]) + 1
                    total_albums[song_album][1] = int(total_albums[song_album][1]) + song_played_time
                
                # get variables of latest date taken into account
                last_date_epoch = datetime.datetime.timestamp(song_date)
                last_date = song_date.timetuple()

        except KeyError: 
            # that means that the song isn't well written, it could be because it's the last song from ASS-log files
            # since the script doesn't write the last song ms_played until another song is played
            pass
    try:
        #set up for display
        total_time = total_time/1000 # convert ms to s
        day_delta = (last_date_epoch-first_date_epoch)/86400 # time delta divided by s into days

        min, s = divmod(total_time, 60)
        h, min = divmod(min, 60)
        d, h = divmod(h, 24)
        d, h, min, s = int(d), int(h), int(min), int(s)

        #sort dict by streamed time
        total_unique_tracks = dict(sorted(total_unique_tracks.items(), reverse=True, key=lambda item: item[1][1])) 
        total_artists = dict(sorted(total_artists.items(), reverse=True, key=lambda item: item[1][1]))
        total_albums = dict(sorted(total_albums.items(), reverse=True, key=lambda item: item[1][1]))

        #display initialization
    
        display_date_window = f"Data from {first_date[2]} {list(calendar.month_name)[int(first_date[1])]} {(first_date[0])} to {last_date[2]} {list(calendar.month_name)[int(last_date[1])]} {(last_date[0])} ({int(day_delta)} days)."
        display_total_time = f"\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}TOTAL TIME STREAMED{Style.RESET_ALL}\n\n| {(d*24+h)*60+min} minutes \n| {d*24+h} hours \n| {d} days"
        display_average_time = f"\n{"="*50}\n\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}AVERAGE DAILY TIME{Style.RESET_ALL}\n\n| {int(((d*24+h)*60+min)/(day_delta))} minutes/day \n| {int(total_streams/(day_delta))} streams/day"
        display_total_streams = f"\n{"="*50}\n\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}STREAMS{Style.RESET_ALL} | {total_streams}"
        display_total_unique_tracks = f"\n{"="*50}\n\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}DIFFERENT TRACKS{Style.RESET_ALL} | {len(total_unique_tracks)} ({int(len(total_unique_tracks)/total_streams*100)}%)"
        display_total_artists = f"\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}DIFFERENT ARTISTS{Style.RESET_ALL} | {len(total_artists)}"
        display_total_albums = f"\n{Style.BRIGHT}{Fore.LIGHTGREEN_EX}DIFFERENT ALBUMS{Style.RESET_ALL} | {len(total_albums)}"
        display_top_tracks = f"\n{"="*50}\n\n{Fore.BLUE}=========={Style.RESET_ALL}\n{Style.BRIGHT}TOP TRACKS{Style.RESET_ALL}\n{Fore.BLUE}=========={Style.RESET_ALL}\n"
        display_top_artists = f"\n\n{Fore.BLUE}==========={Style.RESET_ALL}\n{Style.BRIGHT}TOP ARTISTS{Style.RESET_ALL}\n{Fore.BLUE}==========={Style.RESET_ALL}\n"
        display_top_albums = f"\n\n{Fore.BLUE}=========={Style.RESET_ALL}\n{Style.BRIGHT}TOP ALBUMS{Style.RESET_ALL}\n{Fore.BLUE}=========={Style.RESET_ALL}\n"
    except UnboundLocalError:
        print(f"{Fore.RED}There is not enough data to display that.{Style.RESET_ALL}")
        time.sleep(2)
        System.Clear()
        Page()
        Where()
    except Exception as e:
        print(f"{Fore.RED}An error may have occured. ({e}){Style.RESET_ALL}")
        time.sleep(2)
        System.Clear()
        Page()
        Where()

    #display print
    print(Box.Lines("\n"+type+" STATISTICS"+"\n"))
    print(Center.XCenter(display_date_window))
    print((display_total_time))
    print((display_average_time))
    print((display_total_streams))
    print((display_total_unique_tracks))
    print((display_total_artists))
    print((display_total_albums))

    # TOP TRACKS
    i=0
    while i < 10:
        track_name = list(total_unique_tracks.keys())[i]
        track_artist = total_unique_tracks[track_name][2]
        if len(track_name) > 40:
            try:
                track_name_display = track_name[0:track_name.index(" ", 40)]+"..."
            except:
                track_name_display = track_name
        else:
            track_name_display = track_name
        if i+1 == 10: 
            display_top_tracks += f"\n#{i+1} - {track_name_display} {Style.DIM}by {track_artist}{Style.RESET_ALL} " + f"{Fore.CYAN}({int(total_unique_tracks[track_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        else: # add one more space so that evertyhing is aligned
            display_top_tracks += f"\n#{i+1}  - {track_name_display} {Style.DIM}by {track_artist}{Style.RESET_ALL} " + f"{Fore.CYAN}({int(total_unique_tracks[track_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        i += 1
    print((display_top_tracks))

    # TOP ARTISTS
    i=0
    while i < 10:
        artist_name = list(total_artists.keys())[i]
        if i+1 == 10: 
            display_top_artists += f"\n#{i+1} - {artist_name} " + f"{Fore.CYAN}({int(total_artists[artist_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        else:
            display_top_artists += f"\n#{i+1}  - {artist_name} " + f"{Fore.CYAN}({int(total_artists[artist_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        i += 1
    print((display_top_artists))

    # TOP ALBUMS
    i=0
    while i < 10:
        album_name = list(total_albums.keys())[i]
        album_artist = total_albums[album_name][2]
        if len(album_name) > 40:
            try:
                album_name_display = album_name[0:album_name.index(" ", 40)]+"..."
            except:
                album_name_display = album_name
        else:
            album_name_display = album_name
        if i+1 == 10: 
            display_top_albums += f"\n#{i+1} - {album_name_display} {Style.DIM}by {album_artist}{Style.RESET_ALL} " + f"{Fore.CYAN}({int(total_albums[album_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        else:
            display_top_albums += f"\n#{i+1}  - {album_name_display} {Style.DIM}by {album_artist}{Style.RESET_ALL} " + f"{Fore.CYAN}({int(total_albums[album_name][1]/1000//60)} minutes){Style.RESET_ALL}" + " "
        i += 1
    print((display_top_albums))

    Where()

if __name__ == "__main__":
    os.system("cls")
    Page()
    Where()