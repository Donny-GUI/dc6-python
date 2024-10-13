import struct
from io import BytesIO
from typing import List, Optional
import numpy as np  # For handling the color palette
from PIL import Image

# Constants
END_OF_SCANLINE = 0x80
MAX_RUN_LENGTH = 0x7F
TERMINATOR_SIZE = 3

# Scanline states
class ScanlineState:
    END_OF_LINE = 0
    RUN_OF_TRANSPARENT_PIXELS = 1
    RUN_OF_OPAQUE_PIXELS = 2

class Frame:
    def __init__(self):
        self.Flipped: int = 0
        self.Width: int = 0
        self.Height: int = 0
        self.OffsetX: int = 0
        self.OffsetY: int = 0
        self.Unknown: int = 0
        self.NextBlock: int = 0
        self.Length: int = 0
        self.FrameData: bytes = b''
        self.Terminator: bytes = b''
        self.IndexData: Optional[bytes] = None

    def decode_frame(self) -> None:
        """
        Decodes the frame data from the DC6 format into an index data array.

        The DC6 format stores frame data in a compressed format, which is
        decoded into an index data array by this method.

        The index data array is a 1-dimensional array of bytes, where each
        byte represents the index of a color in the color palette.

        This method decodes the frame data by iterating over the FrameData
        bytes and determining the type of scanline represented by each byte.
        There are three types of scanlines: End of Line, Run of Transparent
        Pixels, and Run of Opaque Pixels.

        For each scanline, the relevant information is extracted from the
        FrameData and used to populate the index data array.

        :return: None
        """

        # Initialize an empty index data array with the correct size
        index_data = bytearray(self.Width * self.Height)

        # Initialize the x and y coordinates to the top-left of the frame
        x = 0
        y = self.Height - 1

        # Initialize the offset to the first byte of the FrameData
        offset = 0

        # Loop until we've processed all the FrameData bytes
        while True:
            
            # If we've reached the end of the FrameData, break out of the loop
            if offset >= len(self.FrameData):
                break

            # Get the next byte from the FrameData
            b = self.FrameData[offset]
            offset += 1

            # Determine the type of scanline represented by this byte
            scanline_type = self.get_scanline_type(b)

            # If this is an End of Line scanline, move to the next line
            if scanline_type == ScanlineState.END_OF_LINE:
                
                # If we've reached the top of the frame, break out of the loop
                if y < 0:
                    break
                
                # Move to the next line
                y -= 1
                x = 0
                
            # If this is a Run of Transparent Pixels scanline, advance the x coordinate
            elif scanline_type == ScanlineState.RUN_OF_TRANSPARENT_PIXELS:
                # Get the number of transparent pixels from the byte
                transparent_pixels = b & MAX_RUN_LENGTH

                # Advance the x coordinate by the number of transparent pixels
                x += transparent_pixels
                
            # If this is a Run of Opaque Pixels scanline, populate the index data array
            elif scanline_type == ScanlineState.RUN_OF_OPAQUE_PIXELS:
                
                # Loop until we've processed all the pixels in the run
                for _ in range(b):
                    
                    # If we've reached the end of the FrameData, break out of the loop
                    if offset >= len(self.FrameData):
                        break  # Prevent reading beyond FrameData
                    
                    # Get the index of the color from the FrameData
                    index_data[x + y * self.Width] = self.FrameData[offset]
                    offset += 1
                    x += 1

        # Set the IndexData property to the completed index data array
        self.IndexData = bytes(index_data)

    def get_scanline_type(self, b: int) -> int:
        """
        Determine the type of scanline given the byte value.

        Given a single byte from the frame data, this function returns the type of scanline
        represented by that byte.

        :param b: The byte from the frame data to determine the scanline type from
        :return: The type of scanline represented by the given byte
        :rtype: int
        """
        # If the byte is equal to END_OF_SCANLINE, then it's an End of Line scanline
        if b == END_OF_SCANLINE:
            return ScanlineState.END_OF_LINE

        # If the byte has the high bit set, then it's a Run of Transparent Pixels scanline
        # This is determined by performing a bitwise AND with the END_OF_SCANLINE constant
        elif (b & END_OF_SCANLINE) > 0:
            return ScanlineState.RUN_OF_TRANSPARENT_PIXELS

        # If the byte doesn't match either of the above criteria, then it's a Run of Opaque Pixels
        # scanline
        return ScanlineState.RUN_OF_OPAQUE_PIXELS

        # The three types of scanlines are as follows:
        #
        # 1. End of Line: A single byte with the value of END_OF_SCANLINE
        # 2. Run of Transparent Pixels: A byte with the high bit set and a value between 0 and MAX_RUN_LENGTH
        # 3. Run of Opaque Pixels: A byte with a value between 0 and MAX_RUN_LENGTH
    
    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the Frame object.

        :return: A dictionary containing the Frame object's properties
        :rtype: dict
        """
        return {
            "Flipped":self.Flipped,
            "Width":self.Width,
            "Height":self.Height,
            "OffsetX":self.OffsetX,
            "OffsetY":self.OffsetY,
            "Unknown":self.Unknown,
            "NextBlock":self.NextBlock,
            "Length":self.Length,
            "FrameData":self.FrameData,
            "Terminator":self.Terminator,
            "IndexData":self.IndexData,
        }


class Direction:
    def __init__(self):
        """
        Initializes a new instance of the Direction class.

        The Direction class represents a single direction in a DC6 animation. This
        class contains a list of frames, each represented by a Frame object.

        :ivar Frames: A list of frames for the direction
        :type Frames: List[Frame]
        """
        self.Frames: List[Frame] = []
    
    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the Direction object.

        :return: A dictionary containing the Direction object's properties
        :rtype: dict
        """
        return {frame.as_dict() for frame in self.Frames}


class DC6:
    def __init__(self):
        """
        Initializes a new instance of the DC6 class.

        The DC6 class represents an entire DC6 animation. This class contains information
        about the animation, such as the version, flags, encoding, and termination. It also
        contains a list of directions, each represented by a Direction object.

        :ivar Version: The version of the DC6 animation format
        :type Version: int
        :ivar Flags: The flags for the animation
        :type Flags: int
        :ivar Encoding: The encoding used for the animation
        :type Encoding: int
        :ivar Termination: The termination bytes for the animation
        :type Termination: bytes
        :ivar Directions: A list of directions in the animation
        :type Directions: List[Direction]
        :ivar palette: The color palette used for the animation. If not set, the default
            palette will be used.
        :type palette: Optional[np.ndarray]
        """
        self.Version: int = 0
        self.Flags: int = 0
        self.Encoding: int = 0
        self.Termination: bytes = b'\x00' * 4
        self.Directions: List[Direction] = []
        self.palette: Optional[np.ndarray] = None
        self.Frames = []
    
    @property
    def frames(self) -> List[dict]:
        """
        Returns a list of all frames in the animation.

        :return: A list of all frames in the animation
        :rtype: List[Frame]
        """
        frames = []
        for direction in self.Directions:
            for frame in direction.Frames:
                frames.append(frame.as_dict())
        return frames
    
    @frames.setter
    def frames(self, new_frames: List[Frame]):
        """
        Sets the frames for the DC6 animation.

        This will replace all existing frames with the provided list.

        :param new_frames: A list of Frame objects to set
        :type new_frames: List[Frame]
        :return: None
        """
        # Clear existing frames
        for direction in self.Directions:
            direction.Frames.clear()

        # Validate new frames
        for frame in new_frames:
            if not isinstance(frame, Frame):
                raise ValueError("All items in new_frames must be instances of Frame.")
            if frame.Width <= 0 or frame.Height <= 0:
                raise ValueError(f"Frame dimensions must be greater than zero: {frame.Width}x{frame.Height}")

        # Populate frames into the first direction for simplicity
        if self.Directions:
            self.Directions[0].Frames.extend(new_frames)
        else:
            # If there are no directions, create one
            new_direction = Direction()
            new_direction.Frames.extend(new_frames)
            self.Directions.append(new_direction)

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Creates a new DC6 object from the given bytes.

        This function takes a byte string containing a DC6 animation and creates a new
        DC6 object from it. The new object will have its properties populated from the
        given data.

        :param data: The DC6 data to create the object from
        :type data: bytes
        :return: The new DC6 object
        :rtype: DC6
        """
        # Create a new instance of the DC6 class
        dc6 = cls()

        # Create a MemoryStream object from the given data. This will allow us to read
        # the data in a stream-friendly way.
        stream = MemoryStream(data)

        # Decode the header of the DC6 animation from the stream. This will populate the
        # Version, Flags, Encoding, and Termination properties of the DC6 object.
        dc6.decode_header(stream)

        # Decode the body of the DC6 animation from the stream. This will populate the
        # Directions list of the DC6 object with Direction objects, and populate the
        # Frames list of each Direction object with Frame objects. It will also decode
        # the frame data for each Frame object.
        dc6.decode_body(stream)

        # Return the new DC6 object
        return dc6

    def decode_header(self, stream:'MemoryStream'):
        """
        Decodes the header of the DC6 animation from the given stream.

        The header of the DC6 animation is 16 bytes long and is formatted as follows:

        - 4 bytes: Version (integer)
        - 4 bytes: Flags (integer)
        - 4 bytes: Encoding (integer)
        - 4 bytes: Termination (4 bytes, always 0)

        :param stream: The stream to read the header from
        :type stream: MemoryStream
        :return: None
        """

        # Read the version of the DC6 animation from the stream. The version is a 4-byte
        # integer, so we use the '<I' format specifier to unpack it.
        version_bytes = 4
        self.Version, = struct.unpack('<i', stream.read(version_bytes))

        # Read the flags of the DC6 animation from the stream. The flags are a 4-byte
        # integer, so we use the '<I' format specifier to unpack it.
        flags_bytes = 4
        self.Flags, = struct.unpack('<I', stream.read(flags_bytes))

        # Read the encoding of the DC6 animation from the stream. The encoding is a 4-byte
        # integer, so we use the '<I' format specifier to unpack it.
        encoding_bytes = 4
        self.Encoding, = struct.unpack('<I', stream.read(encoding_bytes))

        # Read the termination bytes of the DC6 animation from the stream. The termination
        # bytes are always 0, so we don't need to unpack them.
        termination_bytes = 4
        self.Termination = stream.read(termination_bytes)

    def decode_body(self, stream: 'MemoryStream'):
        """
        Decodes the body of the DC6 animation from the given stream.

        This function will populate the Directions list with Direction objects, and
        populate the Frames list of each Direction object with Frame objects. It will
        also decode the frame data for each Frame object.

        The format of the DC6 file is as follows:

        - 4 bytes: The number of directions in the animation (1-255)
        - 4 bytes: The number of frames in each direction (1-255)
        - 4 bytes * (number of directions * number of frames): Frame pointers (ignored)
        - For each frame:
            - 4 bytes: Flipped (0 or 1)
            - 4 bytes: Width (in pixels)
            - 4 bytes: Height (in pixels)
            - 4 bytes: Offset X (in pixels)
            - 4 bytes: Offset Y (in pixels)
            - 4 bytes: Unknown (always 0)
            - 4 bytes: Next Block (always 0)
            - 4 bytes: Frame Length (in bytes)
            - Frame Length bytes: Frame data
            - 3 bytes: Terminator (always 0)

        :param stream: The stream to read the body from
        :type stream: MemoryStream
        :return: None
        """
        directions_bytes = 4
        frames_per_direction_bytes = 4
        frame_pointer_bytes = 4

        # Read the number of directions in the animation
        num_directions, = struct.unpack('<I', stream.read(directions_bytes))

        # Read the number of frames in each direction
        frames_per_direction, = struct.unpack('<I', stream.read(frames_per_direction_bytes))

        # Calculate the total number of frames in the animation
        total_frames = num_directions * frames_per_direction

        # Initialize the Directions list with the correct number of Direction objects
        self.Directions = [Direction() for _ in range(num_directions)]

        # Discard the frame pointers for now
        for _ in range(total_frames):
            stream.read(frame_pointer_bytes)

        # Iterate over each frame in the animation
        for idx in range(total_frames):
            # Calculate the direction and frame indices for this frame
            dir_idx = idx // frames_per_direction
            frame_idx = idx % frames_per_direction

            # Initialize a new Frame object
            frame = Frame()

            # Read the frame data from the stream
            frame.Flipped, = struct.unpack('<I', stream.read(4))
            frame.Width, = struct.unpack('<I', stream.read(4))
            frame.Height, = struct.unpack('<I', stream.read(4))
            frame.OffsetX, = struct.unpack('<i', stream.read(4))
            frame.OffsetY, = struct.unpack('<i', stream.read(4))
            frame.Unknown, = struct.unpack('<I', stream.read(4))
            frame.NextBlock, = struct.unpack('<I', stream.read(4))
            frame.Length, = struct.unpack('<I', stream.read(4))
            frame.FrameData = stream.read(frame.Length)
            frame.Terminator = stream.read(TERMINATOR_SIZE)

            # Add the new frame to the correct direction
            self.Directions[dir_idx].Frames.append(frame)

        # Iterate over each direction in the animation
        for direction in self.Directions:
            # Iterate over each frame in the direction
            for frame in direction.Frames:
                # Decode the frame data
                frame.decode_frame()

    def get_default_palette(self) -> np.ndarray:
        """
        Returns a default palette of 256 gray colors ranging from 0 (black) to 255 (white).

        Each color is represented by 4 bytes: Red, Green, Blue, and Alpha, in that order. The RGB
        values are identical for each color, and the Alpha value is always 255 (fully opaque).

        The palette is a numpy array of shape (256, 4), where each row represents a color and each
        column represents the Red, Green, Blue, and Alpha components of that color, respectively.

        If the palette is not set, this default palette will be used when rendering the animation.

        :return: A numpy array of 256 colors, each represented by 4 bytes (RGB + Alpha)
        :rtype: np.ndarray
        """
        # Initialize the palette array with zeros
        num_colors = 256
        palette = np.zeros((num_colors, 4), dtype=np.uint8)

        # Iterate over each color in the palette
        for idx in range(num_colors):
            # Set the RGB values of this color to the current index
            palette[idx, 0] = idx
            palette[idx, 1] = idx
            palette[idx, 2] = idx

            # Set the Alpha value of this color to 255 (fully opaque)
            palette[idx, 3] = 255

        # Return the completed palette
        return palette

    def set_palette(self, palette: Optional[np.ndarray]):
        """
        Sets the palette for the DC6 animation.

        The palette is a numpy array of 256 colors, each represented by 4 bytes (Red, Green, Blue, and Alpha, in that order).
        The Red, Green, and Blue values are the color components of the pixel, and the Alpha value determines the transparency of the pixel.

        If the palette is not set (i.e. None), a default palette of 256 gray colors will be used
        when rendering the animation. The default palette is created by the get_default_palette method.

        The default palette is a numpy array of shape (256, 4), where each row represents a color and each
        column represents the Red, Green, Blue, and Alpha components of that color, respectively.

        If a custom palette is passed in, it must be a numpy array of shape (256, 4) with the same structure as the default palette.

        :param palette: The palette data as a numpy array of 256 colors, each represented by 4 bytes (RGB + Alpha)
        :type palette: Optional[np.ndarray]
        """
        if palette is None:
            # If the palette is not set, create a default palette of 256 gray colors
            palette = self.get_default_palette()
        self.palette = palette
    
    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the DC6 object.

        :return: A dictionary containing the DC6 object's properties
        :rtype: dict
        """
        return {
            'Version': self.Version,
            'Flags': self.Flags,
            'Encoding': self.Encoding,
            'Termination': self.Termination,
            'Directions': [direction.as_dict() for direction in self.Directions],
            'palette': self.palette.tolist() if self.palette is not None else None,
            "Frames": self.frames,
        }
    
    def dump(self) -> bytes:
        """
        Serializes the DC6 object into a bytes representation according to the DC6 format.

        :return: A bytes object containing the serialized DC6 data
        :rtype: bytes
        """
        # Create a MemoryStream to store the output data
        output_stream = bytearray()

        # Write the header
        output_stream.extend(struct.pack('<I', self.Version))
        output_stream.extend(struct.pack('<I', self.Flags))
        output_stream.extend(struct.pack('<I', self.Encoding))
        output_stream.extend(b'\x00\x00\x00\x00')  # Termination (4 bytes, always 0)

        # Write the number of directions and frames per direction
        num_directions = len(self.Directions)
        frames_per_direction = len(self.Directions[0].Frames) if num_directions > 0 else 0
        output_stream.extend(struct.pack('<I', num_directions))
        output_stream.extend(struct.pack('<I', frames_per_direction))

        # Write frame pointers (ignored, but must be present)
        for _ in range(num_directions * frames_per_direction):
            output_stream.extend(struct.pack('<I', 0))  # Placeholder pointers

        # Write the frame data for each direction and frame
        for direction in self.Directions:
            for frame in direction.Frames:
                # Write the frame properties
                output_stream.extend(struct.pack('<I', frame.Flipped))
                output_stream.extend(struct.pack('<I', frame.Width))
                output_stream.extend(struct.pack('<I', frame.Height))
                output_stream.extend(struct.pack('<i', frame.OffsetX))
                output_stream.extend(struct.pack('<i', frame.OffsetY))
                output_stream.extend(struct.pack('<I', frame.Unknown))
                output_stream.extend(struct.pack('<I', frame.NextBlock))
                output_stream.extend(struct.pack('<I', frame.Length))
                
                # Write the frame data
                output_stream.extend(frame.FrameData)
                
                # Write the terminator
                output_stream.extend(b'\x00\x00\x00')  # Terminator (3 bytes, always 0)

        return bytes(output_stream)
    

class MemoryStream:
    def __init__(self, data: bytes):
        """
        Initializes a new MemoryStream instance with the given data.

        :param data: The data to store in the memory stream
        :type data: bytes
        """
        self.data = data
        self.position = 0

    def read(self, size: int) -> bytes:
        """
        Reads the specified number of bytes from the memory stream 
        and returns them as a byte string.

        The current position of the memory stream is advanced by 
        the number of bytes read.

        This method works by:

        1. Determining the start and end indices of the bytes to read
           from the current position of the memory stream and the
           number of bytes to read.

        2. Returning the bytes between the start and end indices as
           a byte string.

        3. Updating the current position of the memory stream to the
           end index.

        :param size: The number of bytes to read
        :type size: int
        :return: The read bytes as a byte string
        :rtype: bytes
        """
        # Determine the start and end indices of the bytes to read
        start = self.position
        end = start + size

        # Read the bytes from the memory stream
        data = self.data[start:end]

        # Advance the current position of the memory stream
        self.position = end

        # Return the read bytes
        return data


class DC6File(DC6):
    def __init__(self, file_path: str):
        """
        Initializes a new DC6File instance with the given file path.

        This function works by:

        1. Opening the file at the specified path in binary read mode ('rb') using a with statement. 
           This ensures that the file is properly closed after it is read.

        2. Reading the contents of the file into a byte string using the read() method.

        3. Creating a new DC6File instance from the byte string using the from_bytes() class method.

        4. Returning the new DC6File instance.

        :param file_path: The path to the DC6 file to read
        :type file_path: str
        """
        with open(file_path, 'rb') as file:
            # Read the contents of the file into a byte string
            data = file.read()

        # Create a new DC6File instance from the byte string
        dc6 = DC6.from_bytes(data)

        # Return the new DC6File instance
        super().__init__(dc6)
    
    def save_frames(self, output_dir: str):
        """
        Saves all frames in the DC6 animation to separate PNG files in the specified output directory.

        This function works by iterating over all frames in the animation and saving each frame as a separate PNG file in the specified output directory.
        The filename of each PNG file is of the form "frame_dirX_frameY.png", where X is the direction index and Y is the frame index.

        The process works as follows:

        1. Iterate over all directions in the animation.
        2. Iterate over all frames in the current direction.
        3. Convert the index data of the current frame to an image.
        4. Save the image to a file in the output directory.

        :param output_dir: The directory to save the frames to
        :type output_dir: str
        """
        import os

        # Check if the output directory exists, and create it if it doesn't
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize a counter to keep track of how many frames were saved
        frame_count = 0

        # Iterate over all directions in the animation
        for direction_idx, direction in enumerate(self.Directions):
            # Iterate over all frames in the current direction
            for frame_idx, frame in enumerate(direction.Frames):
                # Check if the frame has index data
                if frame.IndexData is not None:
                    # Convert the index data of the current frame to an image
                    image = Image.new("RGBA", (frame.Width, frame.Height))
                    pixels = image.load()

                    # Iterate over all pixels in the frame
                    for y in range(frame.Height):
                        for x in range(frame.Width):
                            # Get the index of the current pixel
                            index = frame.IndexData[x + y * frame.Width]

                            # Get the color of the current pixel from the palette
                            color = self.palette[index]

                            # Set the color of the current pixel in the image
                            pixels[x, y] = (color[0], color[1], color[2], color[3])  # RGBA

                    # Save the image to a file in the output directory
                    frame_filename = f"frame_dir{direction_idx}_frame{frame_idx}.png"
                    image.save(os.path.join(output_dir, frame_filename))

                    # Increment the frame counter
                    frame_count += 1

        # Print a message to the console indicating how many frames were saved
        print(f"Saved {frame_count} frames to '{output_dir}'.")
    
    def to_bytes(self) -> bytes:
        """
        Converts the DC6File instance to a byte string.

        This function works by serializing the DC6File instance into a byte string using the to_bytes() method of the DC6 class.

        :return: The serialized DC6File instance as a byte string
        :rtype: bytes
        """

        # Start with a bytearray for efficiency
        output = bytearray()

        # Header
        output.extend(struct.pack('<i', self.Version))
        output.extend(struct.pack('<I', self.Flags))
        output.extend(struct.pack('<I', self.Encoding))
        output.extend(self.Termination)

        # Body
        num_directions = len(self.Directions)
        frames_per_direction = max(len(direction.Frames) for direction in self.Directions) if self.Directions else 0

        output.extend(struct.pack('<I', num_directions))
        output.extend(struct.pack('<I', frames_per_direction))

        # Frame pointers (currently just placeholders)
        for _ in range(num_directions * frames_per_direction):
            output.extend(struct.pack('<I', 0))  # Placeholder for frame pointers

        # Encode frames
        for direction in self.Directions:
            for frame in direction.Frames:
                output.extend(struct.pack('<I', frame.Flipped))
                output.extend(struct.pack('<I', frame.Width))
                output.extend(struct.pack('<I', frame.Height))
                output.extend(struct.pack('<i', frame.OffsetX))
                output.extend(struct.pack('<i', frame.OffsetY))
                output.extend(struct.pack('<I', frame.Unknown))
                output.extend(struct.pack('<I', frame.NextBlock))
                output.extend(struct.pack('<I', frame.Length))
                output.extend(frame.FrameData)
                output.extend(frame.Terminator)

        return bytes(output)


        
def load(filepointer) -> DC6:
    """
    Reads a DC6 file from the specified file pointer and returns a DC6 instance.

    This function works by reading the data from the file pointer and then passing it to the DC6.from_bytes() function.

    :param filepointer: The file pointer to read the DC6 file from
    :return: The DC6 instance representing the read DC6 file
    """
    data = filepointer.read()
    if isinstance(data, bytes):
        return DC6.from_bytes(data)
    elif isinstance(data, bytearray):
        return DC6.from_bytes(bytes(data))
    else:
        raise TypeError(f"Expected bytes or bytearray, got {type(data)}")

def dump(dc6: DC6, filepointer:BytesIO) -> None:
    """
    Writes a DC6 file to the specified file pointer.

    This function works by first converting the DC6 instance to a byte string using the to_bytes() method, and then writing the byte string to the file pointer.

    :param dc6: The DC6 instance to write
    :param filepointer: The file pointer to write the DC6 file to
    """
    data = dc6.dump()
    if isinstance(data, bytes):
        filepointer.write(data)
    elif isinstance(data, bytearray):
        filepointer.write(bytes(data))
        


def read_dc6_file(file_path: str) -> DC6:
    """
    Reads a DC6 file from the specified file path and returns a DC6 instance.

    This function works by:

    1. Opening the file at the specified path in binary read mode ('rb') using a with statement. This ensures that the file is properly closed after it is read.

    2. Reading the contents of the file into a byte string using the read() method.

    3. Creating a new DC6 instance from the byte string using the from_bytes() class method.

    4. Returning the new DC6 instance.

    :param file_path: The path to the DC6 file to read
    :type file_path: str
    :return: An instance of the DC6 class
    :rtype: DC6
    """
    with open(file_path, 'rb') as file:
        # Read the contents of the file into a byte string
        data = file.read()

    # Create a new DC6 instance from the byte string
    dc6 = DC6.from_bytes(data)

    # Return the new DC6 instance
    return dc6



