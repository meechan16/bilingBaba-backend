import barcode
from barcode.writer import ImageWriter
import io


def generate_barcode_blob(data, barcode_format='code128', options=None):
    """
    Generates a barcode image as a bytestream blob.

    Parameters:
    - data (str): The data to encode in the barcode.
    - barcode_format (str): The barcode format (default is 'code128').
    - options (dict): Optional dictionary to customize barcode appearance.

    Returns:
    - bytes: The barcode image as a bytestream blob.
    """
    # Get the barcode class

    data = str(data)
    if len(data) < 10:
        data = "0" * (10-len(data)) + data
        print(data)
    barcode_class = barcode.get_barcode_class(barcode_format)
    barcode_instance = barcode_class(
        data,
        writer=ImageWriter()
    )
    # Default options if not provided
    if options is None:
        options = {
            'module_width': 0.2,  # Default is 0.2
            'module_height': 4.0,  # Default is 15.0
            'quiet_zone': 6.5,  # Default is 6.5
            'font_size': 6,  # Default is 10
            'text_distance': 3.0,  # Default is 5.0
            'background': 'white',  # Default is 'white'
            'foreground': 'black',  # Default is 'black'
            'write_text': True,  # Default is True
            'text': data  # Optional: Custom text below the barcode
        }

    # Create an in-memory bytes buffer
    buffer = io.BytesIO()

    # Write the barcode image to the buffer
    barcode_instance.write(buffer, options)

    # Get the image bytes from the buffer
    image_bytes = buffer.getvalue()

    # Close the buffer
    buffer.close()

    return image_bytes


# Example usage:
data = "123"
barcode_blob = generate_barcode_blob(data)
print(
    f"Generated barcode image as bytestream blob: {barcode_blob[:20]}... (truncated)")


# import barcode
# from barcode.writer import ImageWriter

# # Choose the barcode format (e.g., 'code128')
# BARCODE_FORMAT = 'code128'

# # The data to be encoded in the barcode
# data = "1234567890"

# # Create the barcode
# barcode_class = barcode.get_barcode_class(BARCODE_FORMAT)
# barcode_instance = barcode_class(
#     data,
#     writer=ImageWriter()
# )

# # Customize barcode appearance
# options = {
#     'module_width': 0.2,  # Default is 0.2
#     'module_height': 4.0,  # Default is 15.0
#     'quiet_zone': 6.5,  # Default is 6.5
#     'font_size': 6,  # Default is 10
#     'text_distance': 3.0,  # Default is 5.0
#     'background': 'white',  # Default is 'white'
#     'foreground': 'black',  # Default is 'black'
#     'write_text': True,  # Default is True
#     'text': data  # Optional: Custom text below the barcode
# }

# # Save the barcode as an image file with options
# filename = barcode_instance.save("custom_barcode", options)

# print(f"Barcode saved as {filename}.png")

# # import EAN13 from barcode module
# from barcode import EAN13

# # import ImageWriter to generate an image file
# from barcode.writer import ImageWriter

# # Make sure to pass the number as string
# number = '5901234123457'

# # Now, let's create an object of EAN13 class and
# # pass the number with the ImageWriter() as the
# # writer
# my_code = EAN13(number, writer=ImageWriter())

# # Our barcode is ready. Let's save it.
# my_code.save("new_code1")
