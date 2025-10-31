import math
import os
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


class Calculations:
    """Class for calculations and determining what type the lcmatch should be."""

    def __init__(self):
        self.text = ""
        self.image_file = None

    # returns values to calculation function below
    def lmatch(self, ZG, ZL, type) -> NDArray | None:
        if np.ndim(ZG) == 0 and np.ndim(ZL) == 0:
            ZG = np.array([ZG], dtype=complex)
            ZL = np.array([ZL], dtype=complex)

        if np.real(ZG) == np.real(ZL):
            X2 = -np.imag(ZL + ZG)[0]
            X1 = np.inf

            return np.array([[X1, 0], [0, X2]])

        if type == "n":
            RG = np.real(ZG)[0]
            XG = np.imag(ZG)[0]
            RL = np.real(ZL)[0]
            XL = np.imag(ZL)[0]

            self.text += f"RG is {RG:.2f} Ohm\n"
            self.text += f"RL is {RL:.2f} Ohm\n"

        else:
            RG = np.real(ZL)[0]
            XG = np.imag(ZL)[0]
            RL = np.real(ZG)[0]
            XL = np.imag(ZG)[0]

            self.text += f"RG is {RL:.2f} Ohm\n"
            self.text += f"RL is {RG:.2f} Ohm\n"

        Q = np.sqrt(RG / RL - 1 + XG**2 / (RG * RL))

        if not np.isreal(Q):
            self.text += f'\nNo real solution of box_type "{type}" exists\n'
            return None

        X1 = (XG + np.array([1, -1]) * Q * RG) / (RG / RL - 1)
        X2 = -(XL + np.array([1, -1]) * Q * RL)

        return np.array([X1, X2])

    # performs all the actual calculations returned to the UI
    def calculations(self, frequency, absZ, phase, toroid) -> str:
        if frequency == 0 and absZ == 0 and phase == 0:
            return "Please enter values!"
        if absZ == 50 and phase == 0:
            return "No matching box required."

        # AL = 280 # in uH/100 turns for small blue ferrite toroid
        # AL = 200 # in uH/100 turns for small blue ferrite toroid
        # AL = 160 # in uH/100 turns for small blue ferrite toroid, 0.5 - 5 MHz
        AL = toroid  # AL = the selected number for the toroid in the UI
        # print("AL: "+str(AL))

        # AL = 140 # in µH/100 turns for large red toroid 2 - 30 MHz

        omega = 2 * np.pi * frequency

        ZG = 50.0 + 1j * 0.0
        ZL = absZ * np.cos(np.deg2rad(phase)) + 1j * absZ * np.sin(np.deg2rad(phase))

        # which box_type of L-section - n or r?
        RG = np.real(ZG)
        XG = np.imag(ZG)
        RL = np.real(ZL)
        XL = np.imag(ZL)

        # select box_type to try (based on the equations above the lmatch function)
        try:
            if (RG > RL and abs(XL) < math.sqrt(RL * (RG - RL))) or (
                RG > RL and abs(XL) > math.sqrt(RL * (RG - RL))
            ):
                type = "n"
            else:
                type = "r"
        # if there's an error, return the error message
        except ValueError as e:
            return str(e)

        # try box_type, if the capacitance/inductance are below 0 then switch box_type
        try:
            X12 = self.lmatch(ZG, ZL, type)  # either 'r' or 'n'
            # print(X12)

            L = X12[1, 1] / omega * 1e6  # inductance in micro Henry
            C = (-1 / X12[0, 1] / omega) * 1e12  # capacitance in pico Farad

            # raise an error if inductance/capacitance is below 0
            if L < 0 or C < 0:
                self.text += f"\nType {type} gives error. Switching box_type.\n"
                msg = "Error: inductance or capacitance is less than 0. Switching \
                    box_type to find alternative solution."
                raise Exception(msg)

            N = np.sqrt(L / AL) * 100  # number of turns

        # switch the box_type if inductance/capacitance are below 0
        except Exception as e:
            print(e)
            type = "n" if type == "r" else "r"

            X12 = self.lmatch(ZG, ZL, type)  # either 'r' or 'n'

            L = X12[1, 1] / omega * 1e6  # inductance in micro Henry
            C = (-1 / X12[0, 1] / omega) * 1e12  # capacitance in pico Farad

            N = np.sqrt(L / AL) * 100  # number of turns

        # if the box_type is n, add a picture of the capacitors across the source input
        # (and print it in the output textbox )
        if type == "n":
            self.text += "\ncapacitors across the source input\n\n"
            # creating the image filepath
            self.image_file = str(
                Path(os.path.realpath(__file__)).parent / "cap_across_source.jpg"
            )

        # otherwise, if the box_type is r, add a picture of the capacitors across the
        # load (and print it in the output textbox)
        elif type == "r":
            self.text += "\ncapacitors across the transducer load\n\n"
            # creating the image filepath
            self.image_file = str(
                Path(os.path.realpath(__file__)).parent / "cap_across_load.jpg"
            )

        # print all the details such as capacitance, inductance, number of turns
        self.text += f"AL value selected = {AL:.2f} \n"
        self.text += f"capacitance = {C:.2f} pF\n"
        self.text += f"inductance = {L:.2f} µH\n"
        self.text += f"number of turns = {N:.1f}\n"
        self.text += "\n\nHold Left-Click and drag to pan the image\n"
        self.text += "Use CTRL+Mouse Wheel to zoom in/out\n"

        return self.text + "\n"
