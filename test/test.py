import serial
import time
import struct
from sympy import symbols, Eq, sqrt, solve
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys

COM_PORT = '/dev/ttyACM0'
BAUD_RATE = 1000000

x1, y1 = 0.045, 0.02
x2, y2 = 0.205, 0.25
x3, y3 = 0.37, 0.02

def calPositionTDOA(t1, t2, t3):
    print("wait....")
    x, y = symbols('x y')
    t12 = (t1 - t2)
    t13 = (t1 - t3)

    del_12 = 343 * t12
    del_13 = 343 * t13

    eq1 = Eq(sqrt((x - x1)**2 + (y - y1)**2) - sqrt((x - x2)**2 + (y - y2)**2), del_12)
    eq2 = Eq(sqrt((x - x1)**2 + (y - y1)**2) - sqrt((x - x3)**2 + (y - y3)**2), del_13)

    solution = solve((eq1, eq2), (x, y))
    return solution

class RealTimePlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time TDOA Position")
        
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        
        # ตั้งค่าขอบเขตของแกน X และ Y ให้กว้าง 41 และสูง 29 หน่วยตามที่ต้องการ
        self.plot_widget.setXRange(0, 45)  # กว้าง 41 หน่วย (20.5 ถึง -20.5)
        self.plot_widget.setYRange(0, 29)  # สูง 29 หน่วย (14.5 ถึง -14.5)
        
        self.plot_widget.setLabel('left', 'Y Position (cm)')
        self.plot_widget.setLabel('bottom', 'X Position (cm)')
        
        self.scatter_plot = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'))
        self.plot_widget.addItem(self.scatter_plot)
        self.data_points = []

        self.add_microphones()

    def add_microphones(self):
        # กำหนดตำแหน่งไมค์ด้วยสี่เหลี่ยมสีฟ้า
        mic_positions = [{'pos': (x1*1e2, y1*1e2), 'brush': pg.mkBrush(0, 0, 255, 150)},
                         {'pos': (x2*1e2, y2*1e2), 'brush': pg.mkBrush(0, 0, 255, 150)},
                         {'pos': (x3*1e2, y3*1e2), 'brush': pg.mkBrush(0, 0, 255, 150)}]
        mic_plot = pg.ScatterPlotItem(size=10, spots=mic_positions)
        self.plot_widget.addItem(mic_plot)

        # เพิ่มป้ายกำกับ
        text1 = pg.TextItem("mic1", color=(0, 0, 255))
        text1.setPos(x1*1e2, y1*1e2)
        self.plot_widget.addItem(text1)
        
        text2 = pg.TextItem("mic2", color=(0, 0, 255))
        text2.setPos(x2*1e2, y2*1e2)
        self.plot_widget.addItem(text2)
        
        text3 = pg.TextItem("mic3", color=(0, 0, 255))
        text3.setPos(x3*1e2, y3*1e2)
        self.plot_widget.addItem(text3)

    def update_position(self, x, y):
        self.data_points.append({'pos': (x, y), 'brush': pg.mkBrush(255, 0, 0, 255)})
        if len(self.data_points) > 3:
            self.data_points.pop(0)
        self.scatter_plot.setData(self.data_points)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlotter()
    window.setMinimumHeight(600)
    window.setMinimumWidth(1000)
    window.show()

    with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
        cursor = 0
        buffer = bytearray(34)
        data = bytearray(13)
        flag = False
        pt = 0

        while True:
            while True:
                if ser.in_waiting > 0:
                    byte_data = ser.read()
                    buffer[cursor] = byte_data[0]

                    if cursor == 0 and buffer[cursor] != 35:
                        break

                    if (buffer[cursor - 16] == 35 and buffer[cursor - 15] == 102 and buffer[cursor - 1] == 13 and buffer[cursor] == 10):
                        j = 14
                        for i in range(0, 13):
                            data[i] = buffer[cursor - j]
                            j -= 1
                       
                        unpacked_data = struct.unpack('>BiiI', data)

                        done = unpacked_data[0]
                        t1 = unpacked_data[1] * 1e-6
                        t2 = unpacked_data[2] * 1e-6
                        t3 = unpacked_data[3] * 1e-6
                    
                        if done == 1 and flag == False:
                            targetPosition = calPositionTDOA(t1, t2, t3)
                           
                            if len(targetPosition) != 0:
                                x_pos = targetPosition[0][0] * 100
                                y_pos = targetPosition[0][1] * 100
                                print(f"x: {x_pos} cm, y: {y_pos} cm")
                                window.update_position(x_pos, y_pos)
                            else:
                                print("Can not calculate position.", targetPosition)

                            flag = True
                            pt = time.time()

                        if flag == True and time.time() - pt >= 1:
                            flag = False
                            print("reset.....")

                        cursor = 0
                        break
                    else:
                        cursor += 1  
                        if cursor >= 34:
                            cursor = 0
            app.processEvents()

if __name__ == "__main__":
    main()