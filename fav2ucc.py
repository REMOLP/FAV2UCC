### fav2ucc.py ###
# Here are the main and important variables and functions regarding the program.
# Separated in it's own file for better readability.
#
# Not every function is used in the end, but I will keep them just in case in the future.
# So no unnecessary issues or suggestions on GitHub please ^-^ 

import requests

### READING CONFIG .INI FILE HERE ###
def readIniConfigFile(iniFile="fav2ucc.config.ini"):
    import configparser
    
    config = configparser.ConfigParser()
    config.read(iniFile)

    return config

loadedIniFile = readIniConfigFile()

### CONFIG VARIABLES HERE ###
# GLOBAL_VIDEO_ALL_PURPOSE_OFFSET = 10/10 # Not used anywhere for now...
GLOBAL_VIDEO_EXT_OUT = loadedIniFile["General"]["global_video_ext_out"]
TEMP_VIDS_FOLDER = loadedIniFile["General"]["temp_vids_folder"]
OUT_VIDS_FOLDER = loadedIniFile["General"]["out_vids_folder"]
USE_TAGS = bool(int(loadedIniFile["General"]["use_tags"]))

### KoboldCPP API ###
def slapMeDaddy(prompt="Hello everyone! My name is Markiplier and today", maxLen=130, tempr=0.75, topP=0.92, stopSeqs=["\nUser:"]):
		url = 'http://localhost:5001/api/v1/generate/'
		headers = {'Content-Type': 'application/json'}
		data = {
		    'n': 1,
		    'max_context_length': 1832,
		    'max_length': maxLen,
		    'rep_pen': 1.1,
		    'temperature': tempr,
		    'top_p': topP,
		    'top_k': 0,
		    'top_a': 0,
		    'typical': 1,
		    'tfs': 0.9,
		    'rep_pen_range': 2048,
		    'rep_pen_slope': 6.8,
		    'sampler_order': [5,0,2,3,1,4,6],
		    'prompt': prompt,
		    'stop_sequence': stopSeqs
		}

		response = requests.post(url, headers=headers, json=data)
		resp = response.json()
		return resp

### HELPER FUNCS ###
def convert_seconds_to_time(seconds):
    import datetime
    time = datetime.datetime.utcfromtimestamp(seconds)
    return time.strftime('%H:%M:%S')

def concatTrimmedInputs(videoFinalOut="FAV2UCC.mp4", inFile="filestomerge.txt"):
    import subprocess
    inFile = TEMP_VIDS_FOLDER+"/"+inFile

    subprocess.call("ffmpeg -hide_banner -safe 0 -f concat -i {} -c:v libx264 -crf 17 -c:a aac -shortest {}/{}".format(inFile, OUT_VIDS_FOLDER, videoFinalOut).split())

def textStartIndex(orgStr, searchedStr):
    start_index = orgStr.find(searchedStr)
    
    if start_index != -1:
        print(f"The substring '{searchedStr}' starts at index {start_index}.")
        return start_index
    else:
        print(f"The substring '{searchedStr}' was not found.")
        return -1

def howManySpacesUntilIndex(string, index):
    count = 0
    for i in range(index):
        if string[i] == ' ':
            count += 1
    return count

def howManySpaces(string):
    count = 0
    for i in range(len(string)):
        if string[i] == ' ':
            count += 1
    return count

def subtractTimestampsPrecise(tsStart, tsEnd):
    from datetime import datetime
    
    format = '%H:%M:%S.%f'
    dtStart = datetime.strptime(tsStart, format)
    dtEnd = datetime.strptime(tsEnd, format)
    dtDiff = dtEnd - dtStart
    hours, remainder = divmod(dtDiff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = dtDiff.microseconds // 1000
    return '{:02d}:{:02d}:{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)


def trimInputClipv3_2(inFile, outFile="SRT__OUT.mp4", startTime="00:00:00.000", endTime="00:00:21.000", firstClip=False):
    import subprocess
    howLongClip = subtractTimestampsPrecise(startTime, endTime)

    inFileUni = inFile.replace("./", "")
    inFileUni = inFileUni.replace(".\\", "")
    inFileUni = inFileUni.split(".")[0]

    if firstClip:
        subprocess.call("ffmpeg -hide_banner -loglevel error -stats -ss {} -i {} -to {} -shortest -c:v libx264 -crf 1 -c:a aac {}/{}".format(startTime, inFile, howLongClip, TEMP_VIDS_FOLDER, outFile))
    else:
        subprocess.call("ffmpeg -hide_banner -loglevel error -stats -ss {} -i {} -to {} -shortest -c:v libx264 -crf 1 -c:a aac {}/{}".format(startTime, inFile, howLongClip, TEMP_VIDS_FOLDER, outFile))

# Function below was used before, but now it is not at all. Keeping it just in case.
# def concatTrimmedInputsv2(videoFinalOut="MVPY__FAV2UCC.mp4", inFiles=[]):
    # if len(inFiles) <= 0:
        # return None
# 
    # from moviepy.video.io.VideoFileClip import VideoFileClip
    # from moviepy.video.compositing.concatenate import concatenate_videoclips
# 
    # mvpyInFiles = []
    # # Load the video files and define the subclip start/end times
    # for i in range(len(inFiles)):
        # mvpyInFiles.append(VideoFileClip(inFiles[i]))
    # 
    # # Concatenate the clips
    # final_clip = concatenate_videoclips(mvpyInFiles)
    # 
    # # Export the final clip to a new file
    # final_clip.write_videofile(videoFinalOut, audio_codec='aac')


# Not used right now anywhere. It was for the whole different prompt and different model.
# def pureAIString(aiStrOut):
    # return aiStrOut.split('"')[1]

### SRT AI summarization functions ###
def noDiacriticSigns(inStr):
		inStr = inStr.replace(".", "")
		inStr = inStr.replace(",", "")
		inStr = inStr.replace("?", "")
		inStr = inStr.replace("!", "")

		return str(inStr)

def srtTimestampsToUniStr(time):
    # Convert SubRipTime object to HH:MM:SS.MMM string format
    return '{:02d}:{:02d}:{:02d}.{:03d}'.format(
        time.hours, time.minutes, time.seconds, time.milliseconds
    )

def getSrtSubs(srt_file, start_id, count):
    import pysrt

    subs = pysrt.open(srt_file)
    end_id = start_id + count - 1
    
    # Check if end_id is greater than the number of subtitles
    if end_id >= len(subs):
        end_id = len(subs) - 1
    
    # Extract the specified range of subtitles
    subtitles = []
    for i in range(start_id-1, end_id):
        subtitle = subs[i]
        subtitles.append((
            subtitle.index,
            srtTimestampsToUniStr(subtitle.start),
            srtTimestampsToUniStr(subtitle.end),
            subtitle.text
        ))
    
    # Return the last index of the subtitle file and the extracted subtitles
    return subs[-1].index, subtitles, subtitles[-1][2]

def process_subtitles(subs):
    subs = pysrt.open(subs)
    result = [[], []]
    for sub in subs:
        start = sub.start.to_time().strftime('%H:%M:%S.%f')
        end = sub.end.to_time().strftime('%H:%M:%S.%f')
        duration_ms = (sub.end - sub.start).total_seconds() * 1000
        words = sub.text.split()
        word_duration_ms = duration_ms / len(words)
        word_timestamps = [int(sub.start.total_seconds() * 1000 + i * word_duration_ms) for i in range(len(words))]
        word_timestamps = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S.%f') for ts in word_timestamps]
        result[0].extend(word_timestamps)
        result[1].extend(words)
    return result


# THe function below is the main magic behind this program honestly next to the LLM output itself :)
# I should probably change the name, but for now let's leave it as is.
# It basically takes the full timestamp and approximately tells where each words starts.
# Once again, approximately. Understood? Okie :3
def convert_to_timestamps(subs):
    from datetime import datetime, timedelta
    
    timestamps = []
    words = []
    for sub in subs:
        start = datetime.strptime(sub[1], '%H:%M:%S.%f')
        end = datetime.strptime(sub[2], '%H:%M:%S.%f')
        duration = (end - start).total_seconds() * 1000
        sentence_words = sub[3].split()
        word_duration = duration / len(sentence_words)
        timestamp_per_word = []
        current_time = start
        for word in sentence_words:
            word_duration = int(round(word_duration))
            timestamp_per_word.append(current_time.strftime('%H:%M:%S.%f')[:-3])
            words.append(word)
            timestamps.append(current_time.strftime('%H:%M:%S.%f')[:-3])
            current_time += timedelta(milliseconds=word_duration)
    return [timestamps, words]


# Function to help offset final clipStartingTS and clipEndingTS variables.
def convertAndAdjustTimestamps(timestamp1, timestamp2, starting_offset_ms, ending_offset_ms=None):
    from datetime import datetime, timedelta
    # Convert the timestamps to datetime objects
    dt1 = datetime.strptime(timestamp1, "%H:%M:%S.%f")
    dt2 = datetime.strptime(timestamp2, "%H:%M:%S.%f")

    # Convert the starting offset to a timedelta object
    starting_offset = timedelta(milliseconds=starting_offset_ms)

    # Add the starting offset to the starting timestamp
    dt1 += starting_offset

    # If ending_offset_ms is not provided, use the same offset as the starting offset
    if ending_offset_ms is None:
        ending_offset_ms = starting_offset_ms

    # Convert the ending offset to a timedelta object
    ending_offset = timedelta(milliseconds=ending_offset_ms)

    # Add the ending offset to the ending timestamp
    dt2 += ending_offset

    # Convert the timestamps back to the desired format
    adjusted_timestamp1 = dt1.strftime("%H:%M:%S.%f")[:-3]
    adjusted_timestamp2 = dt2.strftime("%H:%M:%S.%f")[:-3]

    return adjusted_timestamp1, adjusted_timestamp2

def stringSimilarity(s1, s2):
    import editdistance
    
    distance = editdistance.eval(s1, s2)
    similarity = 1 - (distance / max(len(s1), len(s2)))
    return similarity


def replaceSwearWordsFromSRT(input_file_path, output_file_path):
    import pysrt
    
    subs = pysrt.open(input_file_path)
    for sub in subs:
        sub.text = sub.text.replace("[ __ ]", "****")
    subs.save(output_file_path, encoding='utf-8')


def mergeSrtFiles(directory):
    import re
    import pysrt
    
    # Get all .srt files in the directory
    srt_files = [f for f in os.listdir(directory) if f.endswith('.srt')]

    # Sort the files by part number
    try:
        srt_files.sort(key=lambda f: int(re.findall(r'-p(\d+)\.', f)[0]))
    except (IndexError, ValueError) as e:
        print(f"Error: {e}. Check if the filename syntax is correct.")
        return

    # Merge the subtitle blocks
    merged_subs = pysrt.SubRipFile()
    last_part = None
    last_id = None
    for srt_file in srt_files:
        subs = pysrt.open(os.path.join(directory, srt_file))
        part = int(re.findall(r'-p(\d+)\.', srt_file)[0])
        shift_amount = (part - 1) * 7200 if last_part is not None else 0
        for sub in subs:
            if last_id is not None:
                sub.index = last_id + 1  # Increment the subtitle ID
            sub.shift(seconds=shift_amount)  # Shift the subtitles by the appropriate amount
            merged_subs.append(sub)
            last_id = sub.index  # Store the subtitle ID for the next iteration
        last_part = part

    # Save the merged subtitles to a new file
    merged_subs.save(os.path.join(directory, 'merged_subs.srt'))


### In theory it should be better and take care of some small details, but it messes up more.
### I will try my best to make it work as it should in the future. For now, the old version above.
# def mergeSrtFiles(directory):
    # import re
    # import pysrt
# 
    # # Get all .srt files in the directory
    # srt_files = [f for f in os.listdir(directory) if f.endswith('.srt')]
# 
    # # Sort the files by part number
    # try:
        # srt_files.sort(key=lambda f: int(re.findall(r'-p(\d+)\.', f)[0]))
    # except (IndexError, ValueError) as e:
        # print(f"Error: {e}. Check if the filename syntax is correct.")
        # return
# 
    # # Merge the subtitle blocks
    # merged_subs = pysrt.SubRipFile()
    # last_part = None
    # last_id = None
    # end_time = None
    # for srt_file in srt_files:
        # subs = pysrt.open(os.path.join(directory, srt_file))
        # part = int(re.findall(r'-p(\d+)\.', srt_file)[0])
        # if last_part is None and subs[0].start.seconds > 0:
            # shift_amount = subs[0].start.seconds
        # else:
            # shift_amount = (part - 1) * 7200
        # for sub in subs:
            # if last_id is not None:
                # sub.index = last_id + 1  # Increment the subtitle ID
            # sub.shift(seconds=shift_amount)  # Shift the subtitles by the appropriate amount
            # if end_time is not None and sub.start.seconds < end_time:
                # sub.shift(seconds=end_time - sub.start.seconds)
            # merged_subs.append(sub)
            # last_id = sub.index  # Store the subtitle ID for the next iteration
            # end_time = sub.end.seconds
        # last_part = part

    # Save the merged subtitles to a new file
    # merged_subs.save(os.path.join(directory, 'merged_subs.srt'))
    # pass
