"""Educational File Sharing Protocol for Low-Bandwidth Networks

Core protocol implementation for file sharing over low-bandwidth networks.
Features include chunking, compression, and error recovery.
"""

import hashlib
import zlib
import struct
from enum import Enum
from typing import Tuple, Optional


class ProtocolVersion:
    """Protocol version information."""
    MAJOR = 1
    MINOR = 0
    PATCH = 0

    @classmethod
    def get_version(cls) -> str:
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"


class ChunkSize(Enum):
    """Available chunk sizes for data transmission."""
    SMALL = 1024       # 1 KB for ultra-low bandwidth
    MEDIUM = 4096      # 4 KB for low bandwidth
    LARGE = 16384      # 16 KB for normal bandwidth
    XLARGE = 65536     # 64 KB for high bandwidth


class CompressionLevel(Enum):
    """Compression levels for data reduction."""
    NONE = 0
    LOW = 1
    MEDIUM = 6
    HIGH = 9


class MessageType(Enum):
    """Protocol message types."""
    HANDSHAKE = 0x01
    FILE_REQUEST = 0x02
    FILE_RESPONSE = 0x03
    CHUNK_DATA = 0x04
    CHUNK_ACK = 0x05
    ERROR = 0x06
    COMPLETE = 0x07


class FileMetadata:
    """Metadata for file transfers."""

    def __init__(self, filename: str, filesize: int, checksum: Optional[str] = None):
        self.filename = filename
        self.filesize = filesize
        self.checksum = checksum
        self.chunks = 0

    def calculate_chunks(self, chunk_size: int) -> int:
        """Calculate number of chunks needed for file transfer."""
        import math
        self.chunks = math.ceil(self.filesize / chunk_size)
        return self.chunks


class ProtocolMessage:
    """Protocol message handler for serialization and deserialization."""

    @staticmethod
    def create_handshake(version: str) -> bytes:
        """Create handshake message."""
        msg_type = MessageType.HANDSHAKE.value
        version_bytes = version.encode('utf-8')
        return struct.pack('B', msg_type) + struct.pack('I', len(version_bytes)) + version_bytes

    @staticmethod
    def create_chunk(chunk_index: int, data: bytes, compress: bool = False) -> bytes:
        """Create chunk message with optional compression."""
        msg_type = MessageType.CHUNK_DATA.value
        payload = data
        if compress:
            payload = zlib.compress(data, CompressionLevel.MEDIUM.value)
        compressed_flag = 1 if compress else 0
        header = struct.pack('BIIBq', msg_type, chunk_index, len(payload), compressed_flag, len(data))
        return header + payload

    @staticmethod
    def parse_chunk(message: bytes) -> Tuple[int, bytes, bool]:
        """Parse chunk message and return chunk index, data, and compression flag."""
        msg_type = struct.unpack('B', message[0:1])[0]
        if msg_type != MessageType.CHUNK_DATA.value:
            raise ValueError(f"Invalid message type: {msg_type}")
        chunk_index, payload_len, compressed, original_len = struct.unpack('IBBq', message[1:15])
        payload = message[15:]
        if compressed:
            payload = zlib.decompress(payload)
        return chunk_index, payload, bool(compressed)

    @staticmethod
    def create_error(error_code: int, error_msg: str) -> bytes:
        """Create error message."""
        msg_type = MessageType.ERROR.value
        error_bytes = error_msg.encode('utf-8')
        return struct.pack('BBI', msg_type, error_code, len(error_bytes)) + error_bytes


class FileTransferProtocol:
    """Main protocol handler for file transfers."""

    def __init__(self, chunk_size: ChunkSize = ChunkSize.MEDIUM, compression: bool = True):
        self.chunk_size = chunk_size.value
        self.compression = compression
        self.protocol_version = ProtocolVersion.get_version()

    def calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA256 checksum for data integrity verification."""
        return hashlib.sha256(data).hexdigest()

    def split_file(self, file_data: bytes) -> list:
        """Split file data into chunks."""
        chunks = []
        for i in range(0, len(file_data), self.chunk_size):
            chunks.append(file_data[i:i + self.chunk_size])
        return chunks

    def reassemble_file(self, chunks: list) -> bytes:
        """Reassemble file from chunks."""
        return b''.join(chunks)

    def compress_chunk(self, chunk: bytes) -> bytes:
        """Compress a chunk of data."""
        if self.compression:
            return zlib.compress(chunk, CompressionLevel.MEDIUM.value)
        return chunk

    def decompress_chunk(self, chunk: bytes) -> bytes:
        """Decompress a chunk of data."""
        if self.compression:
            try:
                return zlib.decompress(chunk)
            except zlib.error:
                return chunk
        return chunk

    def verify_transfer(self, original_data: bytes, received_data: bytes) -> bool:
        """Verify file transfer integrity by comparing checksums."""
        original_checksum = self.calculate_checksum(original_data)
        received_checksum = self.calculate_checksum(received_data)
        return original_checksum == received_checksum
