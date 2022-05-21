import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit



def FFT(file_location):
    file = open(file_location, "r")
    data = list()
    for line in file:
        data.append(line)
        data = [line.strip('\n') for line in file]

    data = data[100:]
    n = len(data)

    timestep = 0.000434782608696
    data_fft = np.fft.rfft(data)
    power = np.abs(data_fft)

    freq = np.fft.rfftfreq(len(data), d=timestep)

    return np.sum(np.abs(power[(freq < 80) & (freq > 60)])) / n


cwd = "./PycharmProjects/SensorRecording/venv/Data4/"

matrix = np.zeros(shape = (21, 19))
#
# for i in range(0,10):
for j in range(0,19):
    if j == 0:
        file_location = cwd + str(j) + ".txt"
        print(file_location)
        try:
            matrix[j] = FFT(file_location)
        except FileNotFoundError:
            matrix[j] = 0
    k = j/2
    if k - int(k) ==0:
        k = int(k)

    file_location = cwd + str(j) + ".txt"
    # print(k)

    # print(file_location)
    try:
        matrix[0][j] = FFT(file_location)
        # print(matrix[0][j])
    except FileNotFoundError:
        matrix[0][j] = 0

    # print(matrix)

print(matrix)



# Find the peak frequency: we can focus on only the positive frequencies
pos_mask = np.where(freq > 0)
freqs = freq[pos_mask]
peak_freq = freqs[power[pos_mask].argmax()]
print(peak_freq)


x = np.arange(7)
y = np.arange(11)
xy_mesh = np.meshgrid(x,y)

def gaussian_2d(xy_mesh, offs, amp, xc, yc, sigma_x, sigma_y):
    # unpack 1D list into 2D x and y coords
    # print(xy_mesh.shape)
    (x, y) = xy_mesh

    # make the 2D Gaussian matrix
    gauss = offs + amp * np.exp(-((x - xc) ** 2 / (2 * sigma_x ** 2) + (y - yc) ** 2 / (2 * sigma_y ** 2))) / (
                2 * np.pi * sigma_x * sigma_y)

    # flatten the 2D Gaussian down to 1D
    # print(np.ravel(gauss))
    return np.ravel(gauss)

guess_vals = [25, 25, 5, 4, 4, 4]

xData = np.zeros(shape = (77, 2), dtype = 'float64')
yData = np.zeros(shape = (77, 1), dtype = 'float64')

for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        xData[i+j*7,0] = i
        xData[i+j*7,1] = j
        yData[i+j*7,0] = matrix[i,j]


# curve fit the test data
fittedParameters, pcov = curve_fit(gaussian_2d, xy_mesh, np.ravel(matrix).astype('float64'), p0 = guess_vals)

modelPredictions = gaussian_2d(xy_mesh, *fittedParameters)

absError = modelPredictions - np.ravel(matrix).astype('float64')

fig, ax = plt.subplots(1, 2)

plt.subplot(121)
degrees = np.zeros(shape = (1, 19))
degrees[0] = [x for x in range(0,19)]
plt.plot(degrees[0], matrix[0], "r", label = "CPC1")


# plt.subplot(122)
# plt.imshow(np.abs(absError.reshape(matrix.shape)))
# plt.colorbar()
# plt.show()


###################################################

cwd = "/Users/elefteriubogdan/PycharmProjects/SensorRecording/venv/Data5/"

matrix = np.zeros(shape = (1, 19))
#
# for i in range(0,10):
for j in range(0,19):
    if j == 0:
        file_location = cwd + str(j) + ".txt"
        print(file_location)
        try:
            matrix[j] = FFT(file_location)
        except FileNotFoundError:
            matrix[j] = 0
    k = j/2
    if k - int(k) ==0:
        k = int(k)

    file_location = cwd + str(j) + ".txt"
    # print(k)

    # print(file_location)
    try:
        matrix[0][j] = FFT(file_location)
        # print(matrix[0][j])
    except FileNotFoundError:
        matrix[0][j] = 0



degrees = np.zeros(shape = (1, 19))
degrees[0] = [x for x in range(0,19)]
plt.plot(degrees[0], matrix[0], "g", label = "CPC2")
plt.legend()
plt.title('FoV 2-channel')
plt.xlabel('Degrees')
plt.ylabel('Intensity')
plt.show()

