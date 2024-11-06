from PIL import Image

# Path to the .ico file
ico_path = r'C:\Users\RKPC\Documents\FUS_Instruments\summer_2024\testpad\images\fus_icon_transparent.ico'

# Path to save the .png file
png_path = r'C:\Users\RKPC\Documents\FUS_Instruments\summer_2024\testpad\images\fus_icon_transparent.png'

# Open the .ico file
with Image.open(ico_path) as img:
    # Save as .png file with high resolution
    img.save(png_path, format='PNG')