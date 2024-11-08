import serial
import time
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal

COM_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

Y_MIN, Y_MAX = 0, 3
mic1_data, mic2_data, mic3_data = [], [], []
MAX_DATA_POINTS = 200

FFT_DATA_POINTS = 128
mic1_fft_data, mic2_fft_data, mic3_fft_data = [], [], []

class DataThread(QThread):
    data_signal = pyqtSignal(int, int, int)

    # def run(self):
    #     with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
    #         print("Serial port opened. Waiting for data...")
    #         while True:
    #             if ser.in_waiting > 0:
    #                 data = ser.readline()
    #                 binary_data = ''.join(f'{byte:08b}' for byte in data)
    #                 binary_data = binary_data[4:-8]

    #                 if len(binary_data) >= 36:
    #                     mic1 = int(binary_data[:12], 2)
    #                     mic2 = int(binary_data[12:24], 2)
    #                     mic3 = int(binary_data[24:36], 2)
    #                     self.data_signal.emit(mic1, mic2, mic3)
    def run(self):
        with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
            print("Serial port opened. Waiting for data...")
            mic1, mic2, mic3 = 0, 0, 0
            while True:
                if ser.in_waiting > 0:  
                    data = ser.readline() 
                    binary_data = ''.join(f'{byte:08b}' for byte in data)  
                    
                    binary_data = binary_data[5:-8]  

                    # print(len(binary_data))

                    if(len(binary_data) >= 3):
                        mic1 = int(binary_data[2])
                        mic2 = int(binary_data[1])
                        mic3 = int(binary_data[0])
                        self.data_signal.emit(mic1, mic2, mic3)
                        

    # def run(self):
    #     with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
    #         print("Serial port opened. Waiting for data...")
    #         while True:
    #             if ser.in_waiting > 0:
    #                 data = ser.readline()
    #                 binary_data = ''.join(f'{byte:08b}' for byte in data)
    #                 binary_data = binary_data[4:-8]

    #                 if len(binary_data) >= 36:
    #                     mic1 = int(binary_data[:12], 2)
    #                     mic2 = int(binary_data[12:24], 2)
    #                     mic3 = int(binary_data[24:36], 2)
    #                     self.data_signal.emit(mic1, mic2, mic3)

class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Data Plot")
        self.win.resize(800, 600)
        self.win.setWindowTitle("Real-Time Mic Data with FFT Frequency Display")

        # Plot for Microphone 1 Data
        self.p1 = self.win.addPlot(title="Microphone 1")
        self.p1.setYRange(Y_MIN, Y_MAX)
        self.mic1_curve = self.p1.plot(pen='b')
        self.freq_text1 = pg.TextItem(anchor=(0,1), color='b')
        self.p1.addItem(self.freq_text1)
        
        self.win.nextRow()

        # Plot for Microphone 2 Data
        self.p2 = self.win.addPlot(title="Microphone 2")
        self.p2.setYRange(Y_MIN, Y_MAX)
        self.mic2_curve = self.p2.plot(pen='g')
        self.freq_text2 = pg.TextItem(anchor=(0,1), color='g')
        self.p2.addItem(self.freq_text2)
        
        self.win.nextRow()

        # Plot for Microphone 3 Data
        self.p3 = self.win.addPlot(title="Microphone 3")
        self.p3.setYRange(Y_MIN, Y_MAX)
        self.mic3_curve = self.p3.plot(pen='r')
        self.freq_text3 = pg.TextItem(anchor=(0,1), color='r')
        self.p3.addItem(self.freq_text3)

        self.data_thread = DataThread()
        self.data_thread.data_signal.connect(self.update_data)
        self.data_thread.start()
        self.st = time.time()

    def update_data(self, mic1, mic2, mic3):
        global mic1_data, mic2_data, mic3_data
        global mic1_fft_data, mic2_fft_data, mic3_fft_data

        # Convert 12-bit data to voltage
        mic1_volt = (mic1 / 4095) * 3
        mic2_volt = (mic2 / 4095) * 3
        mic3_volt = (mic3 / 4095) * 3

        # Collect data for plotting
        mic1_data.append(mic1_volt)
        mic2_data.append(mic2_volt)
        mic3_data.append(mic3_volt)

        if len(mic1_data) > MAX_DATA_POINTS:
            mic1_data.pop(0)
            mic2_data.pop(0)
            mic3_data.pop(0)

        mic1_fft_data.append(mic1_volt)
        mic2_fft_data.append(mic2_volt)
        mic3_fft_data.append(mic3_volt)

        if len(mic1_fft_data) > FFT_DATA_POINTS:
            mic1_fft_data.pop(0)
            mic2_fft_data.pop(0)
            mic3_fft_data.pop(0)

        if time.time() - self.st >= 0.01:
            self.mic1_curve.setData(mic1_data)
            self.mic2_curve.setData(mic2_data)
            self.mic3_curve.setData(mic3_data)

            if len(mic1_fft_data) == FFT_DATA_POINTS:
                mic1_fft = np.abs(np.fft.fft(mic1_fft_data))[:FFT_DATA_POINTS // 2]
                mic2_fft = np.abs(np.fft.fft(mic2_fft_data))[:FFT_DATA_POINTS // 2]
                mic3_fft = np.abs(np.fft.fft(mic3_fft_data))[:FFT_DATA_POINTS // 2]

                freqs = np.fft.fftfreq(FFT_DATA_POINTS, d=1 / BAUD_RATE)[:FFT_DATA_POINTS // 2]
                dom_freq1 = freqs[np.argmax(mic1_fft)]
                dom_freq2 = freqs[np.argmax(mic2_fft)]
                dom_freq3 = freqs[np.argmax(mic3_fft)]

                self.freq_text1.setText(f"Dominant Freq: {dom_freq1:.2f} Hz")
                self.freq_text2.setText(f"Dominant Freq: {dom_freq2:.2f} Hz")
                self.freq_text3.setText(f"Dominant Freq: {dom_freq3:.2f} Hz")

            self.st = time.time()

def main():
    app = MainApp()
    app.app.exec_()

if __name__ == "__main__":
    main()
