import serial
import time
import struct
from sympy import symbols, Eq, sqrt, solve
import socket

HOST = '127.0.0.1'  
PORT = 65432      


COM_PORT = '/dev/ttyACM0'  
BAUD_RATE = 1000000

x1, y1 = 0.045, 0.02
x2, y2 = 0.205, 0.25
x3, y3 = 0.37, 0.02



def calPositionTDOA(t1, t2, t3):
    x, y = symbols('x y')

    t12 = (t1 - t2) 
    t13 = (t1 - t3)
    t23 = (t2 - t3)

    # print(f"after {t12:.10f}, {t13:.10f} ,{t23},")
    del_12 = 343 * t12
    del_13 = 343 * t13


    
    eq1 = Eq(sqrt((x - x1)**2 + (y - y1)**2) - sqrt((x - x2)**2 + (y - y2)**2), del_12)
    eq2 = Eq(sqrt((x - x1)**2 + (y - y1)**2) - sqrt((x - x3)**2 + (y - y3)**2), del_13)

    solution = solve((eq1, eq2), (x,y))

    return solution


def main():
    with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
        cursor = 0
        buffer = bytearray(34)
        data = bytearray(13)    #13 + 4
        flag = False
        pt = 0
        while True:
            while True:
                if ser.in_waiting > 0:
                    byte_data = ser.read() 
                    buffer[cursor] = byte_data[0]

                    if cursor == 0 and buffer[cursor] != 35:    # 
                        break

                    #   # f \r \n
                    if (buffer[cursor - 16] == 35 and buffer[cursor - 15] == 102 and buffer[cursor - 1] == 13 and buffer[cursor] == 10): 

                        j = 14
                        for i in range(0, 13):
                            data[i] = buffer[cursor - j]
                            j -=1
                       
                        unpacked_data = struct.unpack('>BiiI', data)

                        done = unpacked_data[0]
                        t1 = unpacked_data[1] * 1e-6
                        t2 = unpacked_data[2] * 1e-6
                        t3 = unpacked_data[3] * 1e-6


                        print(unpacked_data)

                    
                        # if done == 1 and flag == False:
                        #     print("wait....")
                        #     targetPosition = calPositionTDOA(t1, t2, t3)
                           
                        #     if len(targetPosition) != 0:
                        #         print(f"x: {targetPosition[0][0] * 100} cm, y: {targetPosition[0][1] * 100} cm")
                        #     else:
                        #         print("Can not calculate position.", targetPosition)

                        #     flag = True
                        #     pt = time.time()

                        # if flag == True and time.time() - pt >= 1:
                        #     flag = False
                        #     print("reset.....")



                        cursor = 0
                        break
                    else:
                        cursor += 1  
                        if cursor >= 34: 
                            cursor = 0

                

if __name__ == "__main__":
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((HOST, PORT))
    #     s.listen()
    #     print(f"Listening on {HOST}:{PORT}")
        
    #     conn, addr = s.accept()
    #     with conn:
    #         print('Connected by', addr)
    #         while True:
            
    #             message = "x\n" 
    #             conn.sendall(message.encode())
    main()
