# darkou :)

import json
import glob

import calendar
import datetime
import os
import time 

import requests
import dotenv

from tkinter import Tk, filedialog

from pystyle import *
from colorama import Fore, Style

dotenv.load_dotenv() # load .env file for api key

System.Title("Advanced Spotify Statistics")
System.Clear()

Tk().withdraw()

print("Select the folder that contains your .json Extended Streaming History files from Spotify. \nSelecting the root folder will automatically look for a default folder 'history-files'.")

path = filedialog.askdirectory(initialdir=os.path.abspath(os.getcwd()),
                               title='Please select a directory')

System.Clear()

print(f"{Fore.GREEN}\nCrawling through your file(s)... Please wait...{Style.RESET_ALL}")

history_files = sorted(glob.glob(path+"/*.json" if path != os.path.abspath(os.getcwd()).replace("\\", "/") else "./history-files/*.json"), key=lambda file: int(file[file.rindex("_")+1:file.rindex(".")])) # make list of all files (sorted from oldest to most recent)

history = []

for file in history_files: 
    with open(file, 'r', encoding="utf8") as f:
        history += json.load(f) # make list of all song dicts (sorted from oldest to most recent)

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
    r = input(f"{Fore.GREEN}[1] All time\n[2] Year\n[3] Month \n[4] Week \n[5] Custom \n> {Style.RESET_ALL}")

    try:
        r = int(r[0])
    except:
        System.Clear()
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
    elif r == 5:
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
    first = False

    for song in history:
        song_name = song["master_metadata_track_name"]
        song_artist = song["master_metadata_album_artist_name"]
        song_played_time = song["ms_played"]
        
        song_date = datetime.datetime.fromisoformat(song["ts"]) # get song iso time

        if int(time.time())-to_time >= int(datetime.datetime.timestamp(song_date)) >= int(time.time())-from_time:
            if not first: # get variables of first date taken into account
                first_date_epoch = datetime.datetime.timestamp(song_date)
                first_date = song_date.timetuple()
                first = True

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

            # get variables of latest date taken into account
            last_date_epoch = datetime.datetime.timestamp(song_date)
            last_date = song_date.timetuple()

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
    
    #display init
    try:
        display_date_window = f"Data from {first_date[2]} {list(calendar.month_name)[int(first_date[1])]} {(first_date[0])} to {last_date[2]} {list(calendar.month_name)[int(last_date[1])]} {(last_date[0])} ({int(day_delta)} days)."
        display_total_time = f"Total time streamed  :" + f"\n> {(d*24+h)*60+min} minutes \n> {d*24+h} hours \n> {d} days"
        display_average_time = f"Average daily time : \n> {int(((d*24+h)*60+min)/(day_delta))} minutes/day \n> {int(total_streams/(day_delta))} streams/day"
        display_total_streams = f"Streams : {total_streams}"
        display_total_unique_tracks = f"Different tracks : {len(total_unique_tracks)} ({int(len(total_unique_tracks)/total_streams*100)}%)"
        display_total_artists = f"Different artists : {len(total_artists)}"
        display_top_tracks = "Top tracks :"
        display_top_artists = "Top artists :"
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
    print("\n")
    print(Box.DoubleCube(display_total_time))
    print(Box.DoubleCube(display_average_time))
    print(Box.DoubleCube(display_total_streams))
    print(Box.DoubleCube(display_total_unique_tracks))
    print(Box.DoubleCube(display_total_artists))

    # TOP TRACKS
    i=0
    while i < 10:
        track_name = list(total_unique_tracks.keys())[i]
        if i+1 == 10: 
            display_top_tracks += f"\n#{i+1} - {track_name} " + f"({int(total_unique_tracks[track_name][1]/1000//60)} minutes)"
        else: # add one more space so that evertyhing is aligned
            display_top_tracks += f"\n#{i+1}  - {track_name} " + f"({int(total_unique_tracks[track_name][1]/1000//60)} minutes)"
        i += 1
    print(Box.DoubleCube(display_top_tracks))

    # TOP ARTISTS
    i=0
    while i < 10:
        artist_name = list(total_artists.keys())[i]
        if i+1 == 10: 
            display_top_artists += f"\n#{i+1} - {artist_name} " + f"({int(total_artists[artist_name][1]/1000//60)} minutes)"
        else:
            display_top_artists += f"\n#{i+1}  - {artist_name} " + f"({int(total_artists[artist_name][1]/1000//60)} minutes)"
        i += 1
    print(Box.DoubleCube(display_top_artists))

    # print(total_unique_tracks)

    Where()

if __name__ == "__main__":
    os.system("cls")
    Page()
    Where()