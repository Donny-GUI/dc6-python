# dc6-python
This repository provides a Python implementation for reading, manipulating, and writing DC6 file format data, commonly used in Diablo 2 and its modding community. The DC6 format consists of a series of bitmap images used for animated sprites and UI elements in the game.


# dc6

##  Functions

## load

Reads a DC6 file from the specified file pointer and returns a DC6 instance.

This function works by reading the data from the file pointer and then passing it to the DC6.from_bytes() function.

_param filepointer_ The file pointer to read the DC6 file from
_return_ The DC6 instance representing the read DC6 file


## dump

Writes a DC6 file to the specified file pointer.

This function works by first converting the DC6 instance to a byte string using the to_bytes() method, and then writing the byte string to the file pointer.

_param dc6_ The DC6 instance to write
_param filepointer_ The file pointer to write the DC6 file to


## read_dc6_file

Reads a DC6 file from the specified file path and returns a DC6 instance.

This function works by_

1. Opening the file at the specified path in binary read mode ('rb') using a with statement. This ensures that the file is properly closed after it is read.

2. Reading the contents of the file into a byte string using the read() method.

3. Creating a new DC6 instance from the byte string using the from_bytes() class method.

4. Returning the new DC6 instance.

_param file_path_ The path to the DC6 file to read
_type file_path_ str
_return_ An instance of the DC6 class
_rtype_ DC6


##  🏛  Classes

## ScanlineState





## Frame



### __init__


### decode_frame

Decodes the frame data from the DC6 format into an index data array.

The DC6 format stores frame data in a compressed format, which is
decoded into an index data array by this method.

The index data array is a 1-dimensional array of bytes, where each
byte represents the index of a color in the color palette.

This method decodes the frame data by iterating over the FrameData
bytes and determining the type of scanline represented by each byte.
There are three types of scanlines_ End of Line, Run of Transparent
Pixels, and Run of Opaque Pixels.

For each scanline, the relevant information is extracted from the
FrameData and used to populate the index data array.

_return_ None

### get_scanline_type

Determine the type of scanline given the byte value.

Given a single byte from the frame data, this function returns the type of scanline
represented by that byte.

_param b_ The byte from the frame data to determine the scanline type from
_return_ The type of scanline represented by the given byte
_rtype_ int

### as_dict

Returns a dictionary representation of the Frame object.

_return_ A dictionary containing the Frame object's properties
_rtype_ dict



## Direction



### __init__

Initializes a new instance of the Direction class.

The Direction class represents a single direction in a DC6 animation. This
class contains a list of frames, each represented by a Frame object.

_ivar Frames_ A list of frames for the direction
_type Frames_ List[Frame]

### as_dict

Returns a dictionary representation of the Direction object.

_return_ A dictionary containing the Direction object's properties
_rtype_ dict



## DC6



### __init__

Initializes a new instance of the DC6 class.

The DC6 class represents an entire DC6 animation. This class contains information
about the animation, such as the version, flags, encoding, and termination. It also
contains a list of directions, each represented by a Direction object.

_ivar Version_ The version of the DC6 animation format
_type Version_ int
_ivar Flags_ The flags for the animation
_type Flags_ int
_ivar Encoding_ The encoding used for the animation
_type Encoding_ int
_ivar Termination_ The termination bytes for the animation
_type Termination_ bytes
_ivar Directions_ A list of directions in the animation
_type Directions_ List[Direction]
_ivar palette_ The color palette used for the animation. If not set, the default
    palette will be used.
_type palette_ Optional[np.ndarray]

### frames

Returns a list of all frames in the animation.

_return_ A list of all frames in the animation
_rtype_ List[Frame]

### frames

Sets the frames for the DC6 animation.

This will replace all existing frames with the provided list.

_param new_frames_ A list of Frame objects to set
_type new_frames_ List[Frame]
_return_ None

### from_bytes

Creates a new DC6 object from the given bytes.

This function takes a byte string containing a DC6 animation and creates a new
DC6 object from it. The new object will have its properties populated from the
given data.

_param data_ The DC6 data to create the object from
_type data_ bytes
_return_ The new DC6 object
_rtype_ DC6

### decode_header

Decodes the header of the DC6 animation from the given stream.

The header of the DC6 animation is 16 bytes long and is formatted as follows_

- 4 bytes_ Version (integer)
- 4 bytes_ Flags (integer)
- 4 bytes_ Encoding (integer)
- 4 bytes_ Termination (4 bytes, always 0)

_param stream_ The stream to read the header from
_type stream_ MemoryStream
_return_ None

### decode_body

Decodes the body of the DC6 animation from the given stream.

This function will populate the Directions list with Direction objects, and
populate the Frames list of each Direction object with Frame objects. It will
also decode the frame data for each Frame object.

The format of the DC6 file is as follows_

- 4 bytes_ The number of directions in the animation (1-255)
- 4 bytes_ The number of frames in each direction (1-255)
- 4 bytes * (number of directions * number of frames)_ Frame pointers (ignored)
- For each frame_
    - 4 bytes_ Flipped (0 or 1)
    - 4 bytes_ Width (in pixels)
    - 4 bytes_ Height (in pixels)
    - 4 bytes_ Offset X (in pixels)
    - 4 bytes_ Offset Y (in pixels)
    - 4 bytes_ Unknown (always 0)
    - 4 bytes_ Next Block (always 0)
    - 4 bytes_ Frame Length (in bytes)
    - Frame Length bytes_ Frame data
    - 3 bytes_ Terminator (always 0)

_param stream_ The stream to read the body from
_type stream_ MemoryStream
_return_ None

### get_default_palette

Returns a default palette of 256 gray colors ranging from 0 (black) to 255 (white).

Each color is represented by 4 bytes_ Red, Green, Blue, and Alpha, in that order. The RGB
values are identical for each color, and the Alpha value is always 255 (fully opaque).

The palette is a numpy array of shape (256, 4), where each row represents a color and each
column represents the Red, Green, Blue, and Alpha components of that color, respectively.

If the palette is not set, this default palette will be used when rendering the animation.

_return_ A numpy array of 256 colors, each represented by 4 bytes (RGB + Alpha)
_rtype_ np.ndarray

### set_palette

Sets the palette for the DC6 animation.

The palette is a numpy array of 256 colors, each represented by 4 bytes (Red, Green, Blue, and Alpha, in that order).
The Red, Green, and Blue values are the color components of the pixel, and the Alpha value determines the transparency of the pixel.

If the palette is not set (i.e. None), a default palette of 256 gray colors will be used
when rendering the animation. The default palette is created by the get_default_palette method.

The default palette is a numpy array of shape (256, 4), where each row represents a color and each
column represents the Red, Green, Blue, and Alpha components of that color, respectively.

If a custom palette is passed in, it must be a numpy array of shape (256, 4) with the same structure as the default palette.

_param palette_ The palette data as a numpy array of 256 colors, each represented by 4 bytes (RGB + Alpha)
_type palette_ Optional[np.ndarray]

### as_dict

Returns a dictionary representation of the DC6 object.

_return_ A dictionary containing the DC6 object's properties
_rtype_ dict

### dump

Serializes the DC6 object into a bytes representation according to the DC6 format.

_return_ A bytes object containing the serialized DC6 data
_rtype_ bytes



## MemoryStream



### __init__

Initializes a new MemoryStream instance with the given data.

_param data_ The data to store in the memory stream
_type data_ bytes

### read

Reads the specified number of bytes from the memory stream 
and returns them as a byte string.

The current position of the memory stream is advanced by 
the number of bytes read.

This method works by_

1. Determining the start and end indices of the bytes to read
   from the current position of the memory stream and the
   number of bytes to read.

2. Returning the bytes between the start and end indices as
   a byte string.

3. Updating the current position of the memory stream to the
   end index.

_param size_ The number of bytes to read
_type size_ int
_return_ The read bytes as a byte string
_rtype_ bytes



## DC6File



### __init__

Initializes a new DC6File instance with the given file path.

This function works by_

1. Opening the file at the specified path in binary read mode ('rb') using a with statement. 
   This ensures that the file is properly closed after it is read.

2. Reading the contents of the file into a byte string using the read() method.

3. Creating a new DC6File instance from the byte string using the from_bytes() class method.

4. Returning the new DC6File instance.

_param file_path_ The path to the DC6 file to read
_type file_path_ str

### save_frames

Saves all frames in the DC6 animation to separate PNG files in the specified output directory.

This function works by iterating over all frames in the animation and saving each frame as a separate PNG file in the specified output directory.
The filename of each PNG file is of the form "frame_dirX_frameY.png", where X is the direction index and Y is the frame index.

The process works as follows_

1. Iterate over all directions in the animation.
2. Iterate over all frames in the current direction.
3. Convert the index data of the current frame to an image.
4. Save the image to a file in the output directory.

_param output_dir_ The directory to save the frames to
_type output_dir_ str

### to_bytes

Converts the DC6File instance to a byte string.

This function works by serializing the DC6File instance into a byte string using the to_bytes() method of the DC6 class.

_return_ The serialized DC6File instance as a byte string
_rtype_ bytes


