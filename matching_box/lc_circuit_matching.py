from pathlib import Path
import sys
import numpy as np
import math
import os

# from PySide6.QtCore import QObject, Slot
# from PySide6.QtGui import QGuiApplication
# from PySide6.QtQml import QQmlApplicationEngine, QmlElement

# QML_IMPORT_NAME = "print_text"
# QML_IMPORT_MAJOR_VERSION = 1

class Calculations():
    def __init__(self):
        self.text = ""
        self.image_file = None

    def lmatch(self, ZG, ZL, type):
        if np.ndim(ZG) == 0 and np.ndim(ZL) == 0:
            ZG = np.array([ZG], dtype=complex)
            ZL = np.array([ZL], dtype=complex)

        if np.real(ZG) == np.real(ZL):
            X2 = -np.imag(ZL + ZG)[0]
            X1 = np.inf
            # print(X1)
            # print(X2)
            X12 = np.array([[X1, 0],
                            [0, X2]])
            # print(X12)
            return X12

        if type == 'n':
            RG = np.real(ZG)[0]
            XG = np.imag(ZG)[0]
            RL = np.real(ZL)[0]
            XL = np.imag(ZL)[0]
            # print(RG, RL)
            # return([RG, RL])
            self.text += 'RG is %.2f Ohm\n' % RG
            self.text += 'RL is %.2f Ohm\n' % RL

        else:
            RG = np.real(ZL)[0]
            XG = np.imag(ZL)[0]
            RL = np.real(ZG)[0]
            XL = np.imag(ZG)[0]
            # print(RG, RL)
            # return([RL, RG])
            self.text += 'RG is %.2f Ohm\n' % RL
            self.text += 'RL is %.2f Ohm\n' % RG

        Q = np.sqrt(RG / RL - 1 + XG**2 / (RG * RL))

        if not np.isreal(Q):
            self.text += ('\nNo real solution of type "%s" exists\n' % type)
            return

        X1 = (XG + np.array([1, -1]) * Q * RG) / (RG / RL - 1)
        X2 = -(XL + np.array([1, -1]) * Q * RL)
        # print(X1)
        # print(X2)

        X12 = np.array([X1, X2])
        # print(X12)
        return X12
    
    def calculations(self, frequency, absZ, phase, toroid):
        if frequency == 0 and absZ == 0 and phase == 0: 
            return("Please enter values!")
        elif absZ == 50 and phase == 0:
            return("No matching box required.")
        
        # AL = 280 # in uH/100 turns for small blue ferrite toroid
        # AL = 200 # in uH/100 turns for small blue ferrite toroid
        # AL = 160 # in uH/100 turns for small blue ferrite toroid, 0.5 - 5 MHz
        AL = toroid # AL = the selected number for the toroid 
        # print("AL: "+str(AL))

        # AL = 140 # in µH/100 turns for large red toroid 2 - 30 MHz

        omega = 2 * np.pi * frequency

        ZG = 50.0 + 1j * 0.0
        ZL = absZ * np.cos(np.deg2rad(phase)) + 1j * absZ * np.sin(np.deg2rad(phase))

        # which type of L-section - n or r? 
        RG = np.real(ZG)
        XG = np.imag(ZG)
        RL = np.real(ZL)
        XL = np.imag(ZL)

        # select type to try (based on the equations above the lmatch function)
        try:
            if (RG > RL and abs(XL) < math.sqrt(RL*(RG-RL))) or (RG > RL and abs(XL) > math.sqrt(RL*(RG-RL))):
                type = 'n'
            else:
                type = 'r'
        # if there's an error, return the error message 
        except ValueError as e:
            return(str(e))

        # try type, if the capacitance/inductance are below 0 then switch type 
        try:
            X12 = self.lmatch(ZG, ZL, type)  # either 'r' or 'n'
            # print(X12)

            L = X12[1, 1] / omega * 1e6  # inductance in micro Henry
            C = (-1 / X12[0, 1] / omega) * 1e12  # capacitance in pico Farad

            # raise an error if inductance/capacitance is below 0 
            if L < 0 or C < 0: 
                self.text += (f"\nType {type} gives error. Switching type.\n")
                raise Exception("Error: inductance or capacitance is less than 0. Switching type to find alternative solution.")

            N = np.sqrt(L / AL) * 100  # number of turns

        # switch the type if inductance/capacitance are below 0
        except Exception as e:
            print(e)
            if type == 'r':
                type = 'n'
            else:
                type = 'r'

            # textbox.insert(tk.END, f"Switching to Type {type}.\n", "italic")

            X12 = self.lmatch(ZG, ZL, type)  # either 'r' or 'n'

            L = X12[1, 1] / omega * 1e6  # inductance in micro Henry
            C = (-1 / X12[0, 1] / omega) * 1e12  # capacitance in pico Farad

            N = np.sqrt(L / AL) * 100  # number of turns

        # if the type is n, add a picture of the capacitors across the source input (and print it in the output textbox )
        if type == 'n':
            self.text += ('\ncapacitors across the source input\n\n')
            # creating the image filepath
            self.image_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cap_across_source.jpg")
            # print(self.image_file)
            
        # otherwise, if the type is r, add a picture of the capacitors across the load (and print it in the output textbox)
        elif type == 'r':
            self.text += ('\ncapacitors across the transducer load\n\n')
            # creating the image filepath
            self.image_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cap_across_load.jpg")
            # print(self.image_file)

        # print all the details such as capacitance, inductance, number of turns 
        self.text += ('capacitance = %.2f pF\n' % C)
        self.text += ('inductance = %.2f µH\n' % L)
        self.text += ('number of turns = %.1f\n' % N)
        # print(self.text)
        return(self.text + "\n")

# @QmlElement
# class TextBox(QObject): 

#     # @Slot(str, result=str)
#     # def printThing(self, s):
#     #     return(s)
    
#     @Slot(None, result=str) 
#     def getImg(self):
#         return(self.new_calc.image_file)
    
#     @Slot(float, float, float, float, str, result=str)
#     def returnCalc(self, frequency, absZ, phase, toroid, kHz_or_MHz):
#         if kHz_or_MHz == "kHz":
#             frequency *= 1e3
#         else:
#             frequency *= 1e6
#         self.new_calc= Calculations()

#         # print(new_calc)
#         return(self.new_calc.calculations(frequency, absZ, phase, toroid))


# if __name__ == '__main__':
#     #Set up the application window
#     app = QGuiApplication(sys.argv)
#     # view = QQuickView()
#     # view.setResizeMode(QQuickView.SizeRootObjectToView)
#     engine = QQmlApplicationEngine()
#     engine.quit.connect(app.quit)

#     #Load the QML file
#     qml_file = Path(__file__).parent / "widget.qml"
#     engine.load(qml_file)
#     # view.setSource(QUrl.fromLocalFile(qml_file.resolve()))

#     # #Show the window
#     if not engine.rootObjects():
#         sys.exit(-1)
#     # if view.status() == QQuickView.Error:
#     #     sys.exit(-1)
#     # view.show()

#     # #execute and cleanup
#     # app.exec()
#     sys.exit(app.exec())
#     # del view