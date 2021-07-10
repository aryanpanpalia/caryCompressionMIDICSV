import numpy as np
import os

fileFolder = "../1_midicsvtxt_files"
OUTPUT_FOLDER = "../2_carycompressed_files"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pitchCount = 110
filenames = os.listdir(fileFolder)
quantizationSize = 40
minimumPitch = 22

for fileIndex in range(len(filenames)):
    banThisPieceOfMusic = False
    haveSetTempo = False
    currentInstrument = -1
    firstTrackWithNotes = -1
    thisFile = filenames[fileIndex]

    notes = np.zeros((150000, pitchCount), dtype=int)
    allow = np.ones((128,), dtype=bool)
    
    print(f"Starting file {fileIndex} ({fileFolder}/{thisFile})")

    data = open(f"{fileFolder}/{thisFile}").readlines()

    maxPitch = 0
    minPitch = 99999
    finalTime = 0

    for line in data:
        parts = line.split(', ')
        if len(parts) >= 3 and parts[2] == "Tempo":
            if haveSetTempo:
                banThisPieceOfMusic = True
            else:
                division = float(data[0].split(', ')[5])
                tempo = float(parts[3])
                quantizationSize = round((50000.0 / tempo) * division, 1)

        if len(parts) >= 5:
            s = parts[2]
            if s == "Program_c":
                currentInstrument = int(parts[4])
                allow[int(parts[3])] = 0 <= currentInstrument <= 7

        if len(parts) >= 6 and line.find("\"") == -1:
            thisTrack = int(parts[0])
            if allow[int(parts[3])]:
                firstTrackWithNotes = thisTrack
                s = parts[2]
                time = int(int(parts[1]) / quantizationSize)
                inst = int(parts[0])
                pitch = int(parts[4])
                volume = int(parts[5])

                if time < 150000 and inst <= 8:
                    if s == "Note_on_c" and volume >= 1 and notes[time][pitch] == 0:
                        notes[time][pitch] = 1
                        if pitch > maxPitch:
                            maxPitch = pitch
                        if pitch < minPitch:
                            minPitch = pitch
                        if time >= finalTime:
                            finalTime = time
                    elif (s == "Note_on_c" and volume == 0) or s == "Note_off_c":
                        j = time
                        while j >= 0 and notes[j][pitch] % 2 == 0:
                            j -= 1

                        if j >= 0:
                            end = time - 1
                            if end < j + 1:
                                end = j + 1
                            for k in range(j, end):
                                notes[k][pitch] = int(notes[k][pitch] / 2) * 2 + 2
                            if end - 1 >= finalTime:
                                finalTime = end - 1

    if banThisPieceOfMusic:
        print(f"{thisFile} will be aborted")
    else:
        turnedOn = False
        for transposition in range(0, 6):
            open(f"{OUTPUT_FOLDER}/text{fileIndex}_{transposition}.txt", 'w').close()
            output = open(f"{OUTPUT_FOLDER}/text{fileIndex}_{transposition}.txt", 'a')
            for x in range(0, min(150000, finalTime + 24)):
                for y in range(24, pitchCount):
                    if notes[x][y] >= 1:
                        theNum = 33 + (y - minimumPitch + transposition)
                        if 33 <= theNum <= 126:
                            output.write(chr(theNum))
                            turnedOn = True

                if turnedOn:
                    output.write(" ")
                if x % 50 == 49:
                    output.write("\n")

            output.flush()
            output.close()

    print(f"Done with file {fileIndex} ({fileFolder}/{thisFile})")
