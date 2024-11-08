#!/usr/bin/env python3

import numpy as np
from scipy.optimize import least_squares

del_ab,del_ac,del_bc = 0.0000790000, 2.8179560000 ,2.817877



# Microphone positions
x1, y1 = 0.045, 0.02
x2, y2 = 0.205, 0.25
x3, y3 = 0.37, 0.02

# Define the equations
def equations(vars):
    x, y = vars
    eq1 = np.sqrt((x - x1)**2 + (y - y1)**2) - np.sqrt((x - x2)**2 + (y - y2)**2) - del_ab
    eq2 = np.sqrt((x - x1)**2 + (y - y1)**2) - np.sqrt((x - x3)**2 + (y - y3)**2) - del_ac
    eq3 = np.sqrt((x - x2)**2 + (y - y2)**2) - np.sqrt((x - x3)**2 + (y - y3)**2) - del_bc
    return [eq1, eq2, eq3]

# Initial guess
initial_guess = (0, 0)

# Run least squares optimization
result = least_squares(equations, initial_guess)
x, y = result.x

print("x =", x)
print("y =", y)
