# Custom QLineEdit that changes color based on validation
import math

from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QLineEdit


class ValidatedLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Store the original stylesheet
        self.original_style = self.styleSheet()
        # Connect the textChanged signal to the validation function
        self.textChanged.connect(self.validate_input)

    def get_style_property(self, property_name):
        """Helper method to extract specific properties from the stylesheet."""
        style = self.styleSheet()
        start_index = style.find(property_name)
        if start_index == -1:
            return ""
        start_index += len(property_name) + 1  # skip the property name and colon
        end_index = style.find(";", start_index)
        if end_index == -1:
            end_index = len(style)
        return style[start_index:end_index].strip()

    def validate_input(self):
        # Extract the current color and border properties from the stylesheet
        color = self.get_style_property('color')

        # Set valid or invalid color and keep other properties intact
        if self.hasAcceptableInput():
            # If valid, restore the original color (or keep the original border)
            self.setStyleSheet(self.original_style)
        else:
            # If invalid, change only the color to red, leave border unchanged
            new_style = self.original_style
            new_style = f"color: red; {new_style}" if not color else (f"color: red; "
                                                                      f"{new_style.replace(f'color: {color}', '')}")
            self.setStyleSheet(new_style)


# Custom QDoubleValidator that overrides the fixup method
class FixupDoubleValidator(QDoubleValidator):
    def __init__(self, bottom, top, decimals, parent=None):
        super().__init__(bottom, top, decimals, parent)

    def fixup(self, in_str):
        try:
            value = float(in_str)
        except ValueError:
            value = self.bottom()

        factor = 10 ** self.decimals()

        # Calculate the true representable bounds
        actual_bottom = math.ceil(self.bottom() * factor) / factor
        actual_top = math.floor(self.top() * factor) / factor

        # Round input value
        rounded = round(value, self.decimals())

        # Clamp to valid representable range
        clamped = min(max(rounded, actual_bottom), actual_top)

        return f"{clamped:.{self.decimals()}f}"


# Custom QIntValidator that overrides the fixup method
class FixupIntValidator(QIntValidator):
    def __init__(self, bottom, top, parent=None):
        super().__init__(bottom, top, parent)

    def fixup(self, inp):
        # Automatically correct the input to a valid value
        # noinspection PyUnresolvedReferences
        if self.validate(inp, 0)[0] != QIntValidator.State.Acceptable:
            # Convert the input to an integer
            try:
                value = int(inp)
            except ValueError:
                value = self.bottom()  # If conversion fails, use the bottom value

            # Determine the closest valid value (either bottom or top)
            if value < self.bottom():
                inp = str(self.bottom())
            elif value > self.top():
                inp = str(self.top())
            else:
                # If the value is within the valid range, adjust it to the closest integer
                inp = str(value)
        return inp

# Example usage
# self.bbb_start_edit = ValidatedLineEdit(parent=self.bbb_algo_gbox)
# bbb_start_validator = FixupDoubleValidator(0.01, 2.0, 3)  # (bottom, top, decimals)
# self.bbb_start_edit.setText('0.250')
# self.bbb_start_edit.setValidator(bbb_start_validator)
# self.bbb_start_edit.setToolTip('Starting pressure level, from 0.01 to 2.0 MPa')