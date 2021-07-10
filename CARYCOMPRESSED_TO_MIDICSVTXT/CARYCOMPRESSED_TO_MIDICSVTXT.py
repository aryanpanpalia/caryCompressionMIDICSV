import numpy as np
from PIL import Image

INPUT_FILE = "../2_carycompressed_files/text2_1.txt"
OUTPUT_FILE = "../3_reconstructed_midicsvtxt_files/reconstructed_text2_1.txt"
OUTPUT_IMAGE = "../3_reconstructed_midicsvtxt_files/reconstructed_text2_1.png"

pitchCount = 116
# PrintWriter output;
multi = 40

data = open(INPUT_FILE).readlines()
notes = np.zeros((20000, pitchCount), dtype=bool)

pointerAt = 0
for line in data:
	for char in line:
		pitch = ord(char) - 33
		if char == " ":
			pointerAt += 1
		else:
			notes[pointerAt][pitch] = True

pointerAt += 1

outputImage = np.zeros((1080, 1920)).astype('uint8')
shift = 960
for i in range(1000):
	for j in range(87):
		if notes[i + shift][j]:
			outputImage[(86 - j) * 10: (86 - j) * 10 + 10, i * 2: i * 2 + 2] = 255

open(OUTPUT_FILE, 'w').close()
output = open(OUTPUT_FILE, 'a')
output.write("0, 0, Header, 1, 3, 384\n")
output.write("1, 0, Start_track\n")
output.write("1, 0, Time_signature, 4, 2, 24, 8\n")
output.write("1, 0, Tempo, 500000\n")
output.write(f"1, {pointerAt * multi}, End_track\n")
output.write("2, 0, Start_track\n")
output.write("2, 0, Text_t, \"random instrument: random person i dunno whatev\"\n")
output.write("2, 0, Title_t, \"Track 1\"\n")

for i in range(pointerAt):
	for j in range(87):
		if notes[i][j] and (i == 0 or not notes[i - 1][j]):
			output.write(f"2, {i * multi}, Note_on_c, 1, {j + 21}, 127\n")
		if not notes[i][j] and i >= 1 and notes[i - 1][j]:
			output.write(f"2, {i * multi}, Note_off_c, 1, {j + 21}, 0\n")

output.write(f"2, {pointerAt * multi}, End_track\n")
output.write("3, 0, Start_track\n")
output.write("3, 0, Title_t, \"MIDI\"\n")
output.write("3, 1536, End_track\n")
output.write("0, 0, End_of_file\n")
output.flush()
output.close()

image = Image.fromarray(outputImage)
image.save(OUTPUT_IMAGE)
