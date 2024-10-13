# dc6-python
This repository provides a Python implementation for reading, manipulating, and writing DC6 file format data, commonly used in Diablo 2 and its modding community. The DC6 format consists of a series of bitmap images used for animated sprites and UI elements in the game.

# dc6

# 🎈 Functions

###   dc6.load

	- `filepointer`




	Reads a DC6 file from the specified file pointer and returns a DC6 instance.
	
	This function works by reading the data from the file pointer and then passing it to the DC6.from_bytes() function.
	
	:param filepointer: The file pointer to read the DC6 file from
	:return: The DC6 instance representing the read DC6 file


###   dc6.dump

	- `dc6`

	- `filepointer`




	Writes a DC6 file to the specified file pointer.
	
	This function works by first converting the DC6 instance to a byte string using the to_bytes() method, and then writing the byte string to the file pointer.
	
	:param dc6: The DC6 instance to write
	:param filepointer: The file pointer to write the DC6 file to


###   dc6.read_dc6_file

	- `file_path`




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


#  🏛  Classes

## dc6.ScanlineState





## dc6.Frame



### __init__

	

### decode_frame

	
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

### get_scanline_type

	
	Determine the type of scanline given the byte value.
	
	Given a single byte from the frame data, this function returns the type of scanline
	represented by that byte.
	
	:param b: The byte from the frame data to determine the scanline type from
	:return: The type of scanline represented by the given byte
	:rtype: int

### as_dict

	
	Returns a dictionary representation of the Frame object.
	
	:return: A dictionary containing the Frame object's properties
	:rtype: dict



## dc6.Direction



### __init__

	
	Initializes a new instance of the Direction class.
	
	The Direction class represents a single direction in a DC6 animation. This
	class contains a list of frames, each represented by a Frame object.
	
	:ivar Frames: A list of frames for the direction
	:type Frames: List[Frame]

### as_dict

	
	Returns a dictionary representation of the Direction object.
	
	:return: A dictionary containing the Direction object's properties
	:rtype: dict



## dc6.DC6



### __init__

	
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

### frames

	
	Returns a list of all frames in the animation.
	
	:return: A list of all frames in the animation
	:rtype: List[Frame]

### frames

	
	Sets the frames for the DC6 animation.
	
	This will replace all existing frames with the provided list.
	
	:param new_frames: A list of Frame objects to set
	:type new_frames: List[Frame]
	:return: None

### from_bytes

	
	Creates a new DC6 object from the given bytes.
	
	This function takes a byte string containing a DC6 animation and creates a new
	DC6 object from it. The new object will have its properties populated from the
	given data.
	
	:param data: The DC6 data to create the object from
	:type data: bytes
	:return: The new DC6 object
	:rtype: DC6

### decode_header

	
	Decodes the header of the DC6 animation from the given stream.
	
	The header of the DC6 animation is 16 bytes long and is formatted as follows:
	
	- 4 bytes: Version (integer)
	- 4 bytes: Flags (integer)
	- 4 bytes: Encoding (integer)
	- 4 bytes: Termination (4 bytes, always 0)
	
	:param stream: The stream to read the header from
	:type stream: MemoryStream
	:return: None

### decode_body

	
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

### get_default_palette

	
	Returns a default palette of 256 gray colors ranging from 0 (black) to 255 (white).
	
	Each color is represented by 4 bytes: Red, Green, Blue, and Alpha, in that order. The RGB
	values are identical for each color, and the Alpha value is always 255 (fully opaque).
	
	The palette is a numpy array of shape (256, 4), where each row represents a color and each
	column represents the Red, Green, Blue, and Alpha components of that color, respectively.
	
	If the palette is not set, this default palette will be used when rendering the animation.
	
	:return: A numpy array of 256 colors, each represented by 4 bytes (RGB + Alpha)
	:rtype: np.ndarray

### set_palette

	
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

### as_dict

	
	Returns a dictionary representation of the DC6 object.
	
	:return: A dictionary containing the DC6 object's properties
	:rtype: dict

### dump

	
	Serializes the DC6 object into a bytes representation according to the DC6 format.
	
	:return: A bytes object containing the serialized DC6 data
	:rtype: bytes



## dc6.MemoryStream



### __init__

	
	Initializes a new MemoryStream instance with the given data.
	
	:param data: The data to store in the memory stream
	:type data: bytes

### read

	
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



## dc6.DC6File



### __init__

	
	Initializes a new DC6File instance with the given file path.
	
	This function works by:
	
	1. Opening the file at the specified path in binary read mode ('rb') using a with statement.
	This ensures that the file is properly closed after it is read.
	
	2. Reading the contents of the file into a byte string using the read() method.
	
	3. Creating a new DC6File instance from the byte string using the from_bytes() class method.
	
	4. Returning the new DC6File instance.
	
	:param file_path: The path to the DC6 file to read
	:type file_path: str

### save_frames

	
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

### to_bytes

	
	Converts the DC6File instance to a byte string.
	
	This function works by serializing the DC6File instance into a byte string using the to_bytes() method of the DC6 class.
	
	:return: The serialized DC6File instance as a byte string
	:rtype: bytes


