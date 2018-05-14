import csv
import ps_drone
import time
from scipy import signal
import numpy as np
from itertools import islice, chain, repeat
from scipy.fftpack import fft

#------------VARIABLES------------#
chunks = []
chunkslist = []
channel1_chunk = []
channel2_chunk = []
channel1_raw = []
channel2_raw = []
channel3_raw = []
channel4_raw = []
channel5_raw = []
channel6_raw = []
channel7_raw = []
channel8_raw = []
channel1_mean = []
channel2_mean = []
channel3_mean = []
channel4_mean = []
channel5_mean = []
channel6_mean = []
channel7_mean = []
channel8_mean = []
chunks_data = []
baseline_O1 = []
baseline_O2 = []


n = 256
fs = 256
NFFT = 512
hasTakenOff = False
flying = False


#------------FUNCTIONS------------#
def start_drone():
    #Cresting drone instance and starting drone
    drone = ps_drone.Drone()
    drone.startup()

    # Start drone
    drone.trim()
    time.sleep(1)
    drone.takeoff()
    time.sleep(3)

def land_drone():
    drone.stop()
    time.sleep(1)
    drone.land()

#------------READ FROM FILE------------#
#Cresting drone instance and starting drone
drone = ps_drone.Drone()
drone.startup()

# Start drone
drone.trim()
time.sleep(1)


file = raw_input("Please enter the name of file:  ")

with open(file, 'r') as csvfile:
    rawEEG = csv.reader(csvfile)

    # This skips the first row of the CSV file.
    next(rawEEG)

    list = list(rawEEG)

    # Select the data for Channels 1-8
    for row in list:
        arr = row[2:10]

        #Create lists for each
        channel1_raw.append(arr[0])
        channel2_raw.append(arr[1])
        channel3_raw.append(arr[2])
        channel4_raw.append(arr[3])
        channel5_raw.append(arr[4])
        channel6_raw.append(arr[5])
        channel7_raw.append(arr[6])
        channel8_raw.append(arr[7])

    #Convert list to floats
    a = [float(i) for i in channel1_raw]
    b = [float(i) for i in channel2_raw]
    c = [float(i) for i in channel3_raw]
    d = [float(i) for i in channel4_raw]
    e = [float(i) for i in channel5_raw]
    f = [float(i) for i in channel6_raw]
    g = [float(i) for i in channel7_raw]
    h = [float(i) for i in channel8_raw]
    #print type([1])

    #Chop raw data into chunks
    channel1_chunk_total = [a[i * n:(i + 1) * n] for i in range((len(a) + n - 1) // n )]
    channel2_chunk_total = [b[i * n:(i + 1) * n] for i in range((len(b) + n - 1) // n )]
    channel3_chunk_total = [c[i * n:(i + 1) * n] for i in range((len(c) + n - 1) // n )]
    channel4_chunk_total = [d[i * n:(i + 1) * n] for i in range((len(d) + n - 1) // n )]
    channel5_chunk_total = [e[i * n:(i + 1) * n] for i in range((len(e) + n - 1) // n )]
    channel6_chunk_total = [f[i * n:(i + 1) * n] for i in range((len(f) + n - 1) // n )]
    channel7_chunk_total = [g[i * n:(i + 1) * n] for i in range((len(g) + n - 1) // n )]
    channel8_chunk_total = [h[i * n:(i + 1) * n] for i in range((len(h) + n - 1) // n )]

    #Take the mean of the chunks
    for i, obj in enumerate(channel1_chunk_total):
        #print channel1_chunk_total[i]
        channel1_mean.append(np.mean(channel1_chunk_total[i]))
        #print channel1_mean

    for i, obj in enumerate(channel2_chunk_total):
        #print channel1_chunk_total[i]
        channel2_mean.append(np.mean(channel2_chunk_total[i]))
        #print channel2_mean

    for i, obj in enumerate(channel3_chunk_total):
        #print channel1_chunk_total[i]
        channel3_mean.append(np.mean(channel3_chunk_total[i]))
        #print channel3_mean

    for i, obj in enumerate(channel4_chunk_total):
        #print channel1_chunk_total[i]
        channel4_mean.append(np.mean(channel4_chunk_total[i]))
        #print channel4_mean

    for i, obj in enumerate(channel5_chunk_total):
        #print channel1_chunk_total[i]
        channel5_mean.append(np.mean(channel5_chunk_total[i]))
        #print channel5_mean

    for i, obj in enumerate(channel6_chunk_total):
        #print channel1_chunk_total[i]
        channel6_mean.append(np.mean(channel6_chunk_total[i]))
        #print channel6_mean

    for i, obj in enumerate(channel7_chunk_total):
        #print channel1_chunk_total[i]
        channel7_mean.append(np.mean(channel7_chunk_total[i]))
        #print channel7_mean

    for i, obj in enumerate(channel8_chunk_total):
        #print channel1_chunk_total[i]
        channel8_mean.append(np.mean(channel8_chunk_total[i]))
        #print channel8_mean

    #Combine all seconds data into one list
    chunks_list = zip(channel1_mean, channel2_mean, channel3_mean, channel4_mean, channel5_mean, channel6_mean, channel7_mean, channel8_mean)

    #take out the first five and last five seconds
    for i, obj in enumerate(chunks_list):
        end = len(chunks_list) - 5
        chnk = chunks_list[5:end]

    chunks_data = np.asarray(chnk)

    for i, obj in enumerate(chunks_data):
         chunks = chunks_data[i]
         chunks.shape+= (1,)

         #------------SIGNAL PROCESSING FOR CHAANEL------------#

         #1. Compute the PSD
         nbCh, winSampleLength = chunks.shape

         # Apply Hamming window
         w = np.hamming(winSampleLength)
         dataWinCentered = chunks - np.mean(chunks, axis=0) # Remove offset
         dataWinCenteredHam = (dataWinCentered.T*w).T

         #NFFT = nextpow2(winSampleLength)
         Y = np.fft.fft(dataWinCenteredHam, n=NFFT, axis=0)/winSampleLength
         PSD = 2*np.abs(Y[0:NFFT/2,:])
         f = fs/2*np.linspace(0,1,NFFT/2)

         # SPECTRAL FEATURES
         # Average of band powers
         # Delta <4
         ind_delta, = np.where(f<4)
         meanDelta = np.mean(PSD[ind_delta,:],axis=1)
         # Theta 4-8
         ind_theta, = np.where((f>=4) & (f<=8))
         meanTheta = np.mean(PSD[ind_theta,:],axis=1)
         # Alpha 8-12
         ind_alpha, = np.where((f>=8) & (f<=12))
         meanAlpha = np.mean(PSD[ind_alpha,:],axis=1)
         # Beta 12-30
         ind_beta, = np.where((f>=12) & (f<30))
         meanBeta = np.mean(PSD[ind_beta,:],axis=1)

         #------------DRONE CONTROLLER------------#
         O1 = meanAlpha[6]
         O2 = meanAlpha[7]
         if (O2 > 210250.4813274428):
             if hasTakenOff == False:
                 print "Dorne taking off"
                 hasTakenOff = True
                 flying = True
                 drone.takeoff()
                 time.sleep(3)
             if hasTakenOff == True:
                     drone.hover()
                     print "Dorne is hovering"
         elif ( O2 > 140630.28719168712 and O2 < 210250.4813274428):
             if flying == True:
                  print "Dorne is landing"
                  flying = False
                  drone.stop()
                  time.sleep(1)
                  drone.land()
                  drone.trim()
             else:
                  print "Drone has Landed"


         # print (meanAlpha[6], meanAlpha[7])
         time.sleep(1)
         # baseline_O1.append(meanAlpha[6])
         # baseline_O2.append(meanAlpha[7])
# print "O1"
# print "---------------"
# print (min(baseline_O1), max(baseline_O1))
# print ""
# print "O2"
# print "---------------"
# print (min(baseline_O2), max(baseline_O2))
# drone.stop()
# time.sleep(1)
# drone.land()
