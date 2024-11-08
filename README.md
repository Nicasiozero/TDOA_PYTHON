TDOA Positioning System

This project is a TDOA (Time Difference of Arrival) positioning system that calculates the position of a source based on time delays received from three microphones. It uses serial data, calculates position based on TDOA, and provides the data over a WebSocket server.
Requirements

    Operating System: Ubuntu 20.04
    Python Version: Python 3.9

Libraries

Install the required Python libraries by running:

pip install pyserial sympy websockets

Code Overview

    Serial Communication: Reads data from a serial port, configured at 1,000,000 baud rate, using the device /dev/ttyACM0.
    Position Calculation (TDOA): Calculates the source's position (x, y) based on the time delays (t1, t2, t3) from three microphone positions.
    WebSocket Server: The calculated position data is sent to a WebSocket client for real-time display or further processing.

File Structure

    Main Script: This script reads from the serial port, calculates positions, and starts a WebSocket server.
        main(): Serial communication and TDOA calculation.
        calPositionTDOA(): Uses the SymPy library to solve equations for TDOA.
        WSHandler(): WebSocket server function to send position data.
        sendWS(): Initializes and starts the WebSocket server.

Running the Code

    Connect the Serial Device: Ensure the device is connected to /dev/ttyACM0.

    Run the Script: Execute the following command to start the system:

    python3 script_name.py

    Replace script_name.py with the actual name of your script.

    WebSocket Server: The WebSocket server runs on localhost:4000. You can connect to this server to receive real-time position data.

WebSocket Data Format

Data sent over WebSocket:

posX,posY,calculating

    posX and posY: Calculated position in cm.
    calculating: Boolean indicating if a valid position was found.

Example Output

WebSocket server started.
wait....
x: 15.24 cm, y: 5.67 cm
Cannot calculate position.
reset.....

This indicates the calculated (x, y) position or an error if the position couldn't be calculated.
Notes

    Ensure that the serial port configuration and data format match the hardware setup.
    If the WebSocket server address changes, update the HOST and PORT variables in the script.
