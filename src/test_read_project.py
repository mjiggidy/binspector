import struct
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class AVPChunk:
    """Represents a chunk in the AVP file"""
    chunk_type: str
    length: int
    data: bytes
    offset: int  # Where in the file this chunk starts

@dataclass
class AVPProject:
    """Represents an Avid Project file"""
    timestamp: str
    mc_version: str
    chunks: List[AVPChunk]
    settings: Dict[str, Any] = None
    bin_files: List[str] = None

class AVPParser:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.pos = 0
    
    def read_bytes(self, n):
        """Read n bytes and advance position"""
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result
    
    def read_string(self, length):
        """Read a null-terminated or fixed-length string"""
        data = self.read_bytes(length)
        # Try to decode as ASCII, stripping null bytes
        return data.rstrip(b'\x00').decode('ascii', errors='ignore')
    
    def peek_bytes(self, n):
        """Look ahead without advancing position"""
        return self.data[self.pos:self.pos + n]
    
    def read_length_prefixed_string(self):
        """
        Read a string that's prefixed with a 2-byte length.
        
        Teaching moment: Length-prefixed strings are common in binary formats.
        Instead of null-termination, they store the length first, then the string.
        Format: [2 bytes: length] [N bytes: string data]
        """
        length = struct.unpack('<H', self.read_bytes(2))[0]  # H = unsigned short (2 bytes)
        return self.read_string(length)
    
    def parse_header(self):
        """
        Parse the file header.
        
        Teaching moment: Binary files often start with a "magic number" or signature
        that identifies the file type. Here we see "DomainDJBO" and "AObjDoc" which
        are likely Avid's way of marking this as a project file.
        """
        # Read magic strings (each prefixed with 2-byte length)
        # First string: "Domain"
        domain_len = struct.unpack('<H', self.read_bytes(2))[0]
        domain = self.read_string(domain_len)
        
        # Second part: "DJBO" (4 bytes, no length prefix)
        domain_type = self.read_string(4)
        
        # Third string: "AObjDoc"
        obj_len = struct.unpack('<H', self.read_bytes(2))[0]
        obj_type = self.read_string(obj_len)
        
        print(f"Magic: {domain}{domain_type}")
        print(f"Object Type: {obj_type}")
        
        # Read timestamp (also length-prefixed)
        # Format appears to be: [1 byte: 04] [2 bytes: length] [string]
        marker = self.read_bytes(1)  # Should be 0x04
        ts_len = struct.unpack('<H', self.read_bytes(2))[0]
        timestamp = self.read_string(ts_len)
        
        # Skip some unknown bytes 
        # Teaching moment: When reverse engineering, you'll often find bytes
        # whose purpose isn't immediately clear. We skip them for now and can
        # investigate later if needed.
        self.read_bytes(8)
        
        # Skip 4 more bytes (appears to be "IIII" in some files)
        self.read_bytes(4)
        
        # Skip more variable data (looks like UUIDs or identifiers - about 17 bytes)
        self.read_bytes(17)
        
        # Read Media Composer version (length-prefixed with 1 byte: 0x1E = 30)
        version_marker = self.read_bytes(1)  # Should be 0x1E (30)
        mc_version = self.read_string(30).strip()
        
        # Skip more padding - looking for first chunk
        # Teaching moment: Sometimes you need to "scan" forward to find structure
        # We're looking for 4-byte ASCII chunk identifiers like "RTTA", "LTAC"
        while self.pos < len(self.data) - 4:
            peek = self.peek_bytes(4)
            try:
                peek_str = peek.decode('ascii')
                # Check if this looks like a chunk identifier (all printable ASCII uppercase)
                if all(ord('A') <= b <= ord('Z') for b in peek):
                    print(f"Found first chunk '{peek_str}' at offset {self.pos:#x}\n")
                    break
            except:
                pass
            self.pos += 1
        
        return timestamp, mc_version
    
    def parse_chunks(self):
        """
        Parse all chunks in the file.
        
        Teaching moment: Many binary formats use a "chunk" structure:
        - 4 bytes: chunk type identifier (like 'RTTA', 'ELIF')
        - 4 bytes: length of the chunk data
        - N bytes: the actual data
        
        This is called a "TLV" pattern: Type-Length-Value
        """
        chunks = []
        
        while self.pos < len(self.data) - 8:  # Need at least 8 bytes for chunk header
            chunk_start = self.pos
            
            # Read chunk identifier (4 bytes, usually ASCII)
            chunk_id_bytes = self.read_bytes(4)
            try:
                chunk_type = chunk_id_bytes.decode('ascii')
            except:
                # If we can't decode it, we might be at the end or in padding
                break
            
            # Read chunk length (4 bytes, little-endian unsigned int)
            # Teaching moment: '<I' means:
            #   < = little-endian (least significant byte first)
            #   I = unsigned int (4 bytes)
            chunk_length = struct.unpack('<I', self.read_bytes(4))[0]
            
            # Safety check - don't read past end of file
            if self.pos + chunk_length > len(self.data):
                print(f"Warning: Chunk '{chunk_type}' claims length {chunk_length} but only {len(self.data) - self.pos} bytes remain")
                break
            
            # Read chunk data
            chunk_data = self.read_bytes(chunk_length)
            
            chunks.append(AVPChunk(
                chunk_type=chunk_type,
                length=chunk_length,
                data=chunk_data,
                offset=chunk_start
            ))
            
            print(f"Found chunk '{chunk_type}' at offset {chunk_start:#x}, length {chunk_length} bytes")
        
        return chunks
    
    def parse(self):
        """Main parsing function"""
        print(f"Parsing {self.filepath.name}...")
        print(f"File size: {len(self.data)} bytes\n")
        
        timestamp, mc_version = self.parse_header()
        print(f"Timestamp: {timestamp}")
        print(f"Media Composer: {mc_version}\n")
        
        chunks = self.parse_chunks()
        
        print(f"\nFound {len(chunks)} chunks")
        print("\nChunk summary:")
        chunk_types = {}
        for chunk in chunks:
            chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
        
        for chunk_type, count in sorted(chunk_types.items()):
            print(f"  {chunk_type}: {count}")
        
        return AVPProject(
            timestamp=timestamp,
            mc_version=mc_version,
            chunks=chunks
        )

# Example usage
if __name__ == "__main__":
    import sys
    parser = AVPParser(sys.argv[1])
    project = parser.parse()
    print(project)