from PIL import Image
"""
This script converts an .ico file to a .png file using the Python Imaging Library (PIL).
The script performs the following steps:
1. Defines the path to the .ico file.
2. Defines the path to save the .png file.
3. Opens the .ico file.
4. Saves the image as a .png file with high resolution.
Note:
- The file paths for the .ico and .png files are hard-coded and will need to be updated as per your requirements.
Dependencies:
- PIL (Python Imaging Library), which can be installed via the Pillow package.
Usage:
- Update the `ico_path` and `png_path` variables with the appropriate file paths.
- Run the script to convert the .ico file to a .png file.
"""

# Path to the .ico file
ico_path = r'.\fus_icon_transparent.ico'

# Path to save the .png file
png_path = r'.\fus_icon_transparent.png'

# Open the .ico file
with Image.open(ico_path) as img:
    # Save as .png file with high resolution
    img.save(png_path, format='PNG')