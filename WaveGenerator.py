#!/usr/bin/python
"Paul's Acoustic Code Generator"

import wave
import math
import struct
import StringIO
import os

def create_sine_wave(frequency, sampleRate, duration):
    "Create a binary encoded string of 16-bit sine data."
    swave = StringIO.StringIO()
    nPoints = int(round(duration * sampleRate))
    for x in range(nPoints):
        value = math.sin(2*math.pi*frequency*x/sampleRate)
        value = int(value * 32767)  # MAKE IT AN INTEGER
        swave.write(struct.pack('<h', value))  # pack it into a string buffer

    # Return a string containing binary data
    return swave.getvalue()
                            
    
def write_wave_file(filename, signal, sampleRate):
    "Write the data out as a wave file."
    wfile = wave.open(filename, 'wb')

    # Set Parameters (interlace data for multi channels: Left, Right)
    wfile.setnchannels(1)           # 1 Channel (MONO -- not stereo)
    wfile.setsampwidth(2)           # 2-Bytes (16-bits "CD Quality") samples
    wfile.setframerate(sampleRate)  # Sample Rate (samples per second)
    wfile.setnframes(sampleRate*2)  # SampleRate * NumberOfChannels * BytesPerSample
    wfile.setcomptype('NONE', 'noncompressed')  # No compression

    # Write the file
    wfile.writeframes(signal)
    wfile.close()

def get_FSK(code):
    scode = "%d" % code

    tonePairs = [[ 9488,  9901], [ 9488, 10288], [ 9488, 10684], 
                 [ 9901, 10288], [ 9901, 10684], [10288, 10684]]

    octTable = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], 
                [1,0,0], [1,0,1], [1,1,0], [1,1,1]]

    f0, f1 = tonePairs[int(scode[0]) - 1]
    
    binary = []
    for ch in scode[1:]:
        binary = binary + octTable[int(ch)]

    # Add in parity bit
    if (sum(binary)%2 == 0):
        binary = binary + [0,]
    else:
        binary = binary + [1,]

    return (f0, f1, binary)



def createWAV(code, fs):
    (f0, f1, binary) = get_FSK(code)
    wfm = ""
    for n in range(16):
        f = [f0, f1][binary[n]]
        wfm = wfm + create_sine_wave(f, fs, 0.020)  # Tone (20 msec)
        wfm = wfm + create_sine_wave(0, fs, 0.230)  # Delay 230 msec
        if n == 7:
            wfm = wfm + create_sine_wave(0, fs, 5.000) # Delay 5 sec
    wfm = wfm + create_sine_wave(0, fs, 10.000) # Delay 10 sec
    return wfm
	

def create_ping_wave(f, fs):
    wfm = create_sine_wave(f, fs, 0.023); # Ping
    wfm = wfm + (create_sine_wave(0, fs, 5.000)); # delay 5 seconds
    wfm = wfm + (create_sine_wave(f, fs, 0.023)); # Ping
    wfm = wfm + (create_sine_wave(0, fs, 5.000)); # delay 5 seconds
    wfm = wfm + (create_sine_wave(f, fs, 0.023)); # Ping
    wfm = wfm + (create_sine_wave(0, fs, 10.000)); # delay 10 seconds
	
    return wfm

# ====================
# Main Code Generation
# ====================
sampleRate = 44100
dList = [j.split(',') for j in [i.strip() for i in (open("Acoustics.csv", 'rU').readlines())]]
codeNames = dList[0][1:]
print "Generating..."

if not os.path.exists('Wavs'):
    os.makedirs('Wavs')


# Write Ping
wfm = create_ping_wave(11000, sampleRate)
write_wave_file('./Wavs/PING_11KHz.wav', wfm, sampleRate)

# Write Codes
for acoustic in dList[1:]:
    relNum, codes = acoustic[0], acoustic[1:]
    for i,code in enumerate(codes):
        if code != '':
            fname = "./Wavs/R%s_%s_%s.wav" % (relNum, codeNames[i], code)
            print "    %s" % fname
            wfm = createWAV(int(code), sampleRate)
            write_wave_file(fname, wfm, sampleRate)

#sampleRate = 44100   # Audio CD Sample Rate = 44100
#w1 = createWAV(310242, sampleRate)
#write_wave_file('SHIT.WAV', w1, sampleRate)
#n1 = create_sine_wave(261.626, sampleRate, 1) # Middle C for 1 second
#n2 = create_sine_wave(400, sampleRate, .5) # 400 Hz for 1/2 second
#n = n1+n2
#write_wave_file('SHIT.WAVE', n, sampleRate)
