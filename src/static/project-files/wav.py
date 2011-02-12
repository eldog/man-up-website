# Python 3.1
import collections
import struct
import sys

CHUNK_ID_RIFF = b'RIFF'
FORMAT_WAVE = b'WAVE'
SUB_CHUNK_1_ID_FMT = b'fmt '
SUB_CHUNK_2_ID_DATA = b'data'

LINEAR_QUANTIZATION = 1

MONO = 1
STEREO = 2

LEFT_CHANNEL = 0
RIGHT_CHANNEL = 1

class WAVException(Exception):
    pass

class PMC8bitWAV:
    file_spec = collections.OrderedDict()
    file_spec['chunk_id'] = (CHUNK_ID_RIFF, len(CHUNK_ID_RIFF), None)
    file_spec['chunk_size'] = (None, 4, '<I')
    file_spec['format'] = (FORMAT_WAVE, len(FORMAT_WAVE), None)
    file_spec['chunk_size'] = (None, 4, '<I')
    file_spec['sub_chunk_1_id'] = (SUB_CHUNK_1_ID_FMT, len(SUB_CHUNK_1_ID_FMT),
                                   None)
    file_spec['sub_chuck_1_size'] = (16, 4, '<I')
    file_spec['audio_format'] = (LINEAR_QUANTIZATION, 2, '<H')
    file_spec['num_channels'] = (None, 2, '<H')
    file_spec['sample_rate'] = (None, 4, '<I')
    file_spec['byte_rate'] = (None, 4, '<I')
    file_spec['block_align'] = (None, 2, '<H')
    file_spec['bits_per_sample'] = (8, 2, '<H')
    
    file_spec['sub_chunk_2_id'] = (SUB_CHUNK_2_ID_DATA,
                                   len(SUB_CHUNK_2_ID_DATA), None)
    file_spec['sub_chunk_2_size'] = (None, 4, '<I')
    file_spec['data'] = (None, -1, bytearray)
    
    # Don't call the constructor directly. Instead, call PMC8bitWAV.read().
    # Well you can call it if you want, but you need to understand the file_spec
    # dict above.
    def __init__(self, **fields):
        check_fields = {}
        for name, value in fields.items():
            try:
                if hasattr(self, name):
                    raise AttributeError
                setattr(self, name, value)
            except AttributeError:
                check_fields[name] = value
        for name, check_value in check_fields.items():
            value = getattr(self, name)
            if value != check_value:
                raise WAVException('%s should be %r, got %r' 
                    % (name, check_value, value))

    @property
    def block_align(self):
        return self.num_channels * (self.bits_per_sample // 8)
    
    @property
    def byte_rate(self):
        return self.sample_rate * self.num_channels \
            * (self.bits_per_sample // 8)
    
    @property
    def chunk_size(self):
        return 36 + self.sub_chunk_2_size

    @property
    def sub_chunk_2_size(self):
        return len(self.data)
        
    @classmethod
    def read(cls, path):
        fields = {}
        with open(path, 'rb') as wav_file:
            for name, (check_value, num_bytes, fmt) in cls.file_spec.items():
                value = wav_file.read(num_bytes)
                if isinstance(fmt, str):
                    value = struct.unpack(fmt, value)
                    assert len(value) == 1, 'fmt incorrect for %s' % name
                    value = value[0]
                elif fmt is not None:
                    value = fmt(value)
                if check_value is not None and check_value != value:
                    raise WAVException('%s must be %r, got %r'
                                       % (name, check_value, value))
                fields[name] = value
        if len(fields['data']) != fields['sub_chunk_2_size']:
            raise WAVException(
                'length of data does not equal to sub_chunk_2_size')
            
        return cls(**fields)

    def write(self, path):
        with open(path, 'wb') as wav_file:
            for name, (_, _, fmt) in self.file_spec.items():
                value = getattr(self, name)
                if isinstance(fmt, str):
                    value = struct.pack(fmt, value)
                wav_file.write(value)
    
    def channel_delete(self, channel):
        new_data = bytearray()
        for i, byte in enumerate(self.data):
            if i % self.num_channels != channel:
                new_data.append(byte)
        self.data = new_data
        self.num_channels -= 1
    
    # Inverts the phase of the given channel
    def channel_invert(self, channel):
        for i in range(channel, len(self.data), self.num_channels):
            self.data[i] = 255 - self.data[i]       
    
    # Makes the given channel silent
    def channel_silence(self, channel):
        for i in range(channel, len(self.data), self.num_channels):
            self.data[i] = 128
    
    # Copies the source channel to the destination channel
    def channel_copy(self, source, destination):
        offset = destination - source
        for i in range(source, len(self.data), self.num_channels):
            self.data[i + offset] = self.data[i]
    
    # Extracts the stereo difference between two channels and write the result
    # to c1
    def channel_difference(self, c1, c2):
        offset = c2 - c1
        for i in range(c1, len(self.data), self.num_channels):
            diff = 128 + self.data[i + offset] - self.data[i]
            if diff < 0:
                diff = 0
            elif diff > 255:
                diff = 255
            self.data[i] = diff
    
    # Converts the given channel to ASCII, treating bytes of value 128 as ACSII
    # zero. shift is added to each bytes before being converted to ASCII.
    # skip_zeros ignores any bytes that has zero value before being shifted.
    # Odd method to include isn't it :)
    def channel_to_ascii(self, channel, shift=0, skip_zeros=True):
        cs = []
        for i in range(channel, len(self.data), self.num_channels):
            c = self.data[i]
            if not skip_zeros or c != 128:
                cs.append(chr(c - 128 + shift))
        print(''.join(cs))
    
