# Educational File Sharing Protocol for Low-Bandwidth Networks

An educational implementation of a file sharing protocol designed specifically for low-bandwidth network environments. This project demonstrates key concepts in distributed systems, network programming, and data compression techniques.

## Overview

This project provides a complete client-server file sharing system optimized for low-bandwidth networks. It implements features such as:

- File chunking for efficient transmission
- Data compression to reduce bandwidth usage
- Error recovery mechanisms
- Checksum verification for data integrity
- Multi-client support on the server side

## Features

### Core Protocol Features

- **Chunking**: Files are split into configurable chunk sizes (1 KB to 64 KB) for efficient transmission
- **Compression**: Data can be compressed using zlib compression with configurable levels
- **Checksums**: SHA256 checksums verify file integrity after transfer
- **Protocol Versioning**: Supports protocol version negotiation for compatibility
- **Error Handling**: Comprehensive error messages and recovery mechanisms
- **Multi-Client Support**: Server handles multiple concurrent client connections

### Supported Operations

- File download from server
- File upload to server
- File list retrieval
- Protocol handshake and negotiation
- Error recovery and retry logic

## Installation

### Requirements

- Python 3.8 or higher
- No external dependencies required for core functionality

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Aakhil05V/Educational-File-Sharing-Protocol-for-Low-Bandwidth-Networks.git
cd Educational-File-Sharing-Protocol-for-Low-Bandwidth-Networks
```

2. Install dependencies (optional):
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python server.py [host] [port] [data_directory]
```

Example:
```bash
python server.py 0.0.0.0 5000 ./shared_files
```

This will start the server on localhost:5000, serving files from the ./shared_files directory.

### Using the Client

#### Download a file:
```bash
python client.py localhost 5000 download filename.txt
```

#### Upload a file:
```bash
python client.py localhost 5000 upload /path/to/local/file.txt
```

## Project Structure

```
.
├── protocol.py          # Core protocol implementation
├── client.py            # Client implementation
├── server.py            # Server implementation
├── requirements.txt     # Project dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## File Descriptions

### protocol.py

Contains the core protocol implementation including:
- `ChunkSize`: Enumeration of available chunk sizes
- `CompressionLevel`: Enumeration of compression levels
- `MessageType`: Protocol message types
- `FileMetadata`: File metadata handler
- `ProtocolMessage`: Message serialization/deserialization
- `FileTransferProtocol`: Main protocol handler

### client.py

Provides client-side functionality:
- `FileShareClient`: Main client class for connecting to servers
- Connection management
- File download/upload operations
- Protocol handshake

### server.py

Provides server-side functionality:
- `FileShareServer`: Main server class
- Multi-threaded connection handling
- File serving and upload handling
- Request processing and response generation

## How It Works

### Protocol Handshake

1. Client connects to server
2. Client sends handshake message with protocol version
3. Server responds with acknowledgment

### File Download

1. Client sends file request with filename
2. Server validates file exists and is accessible
3. Server splits file into chunks
4. Server sends chunks to client (optionally compressed)
5. Client reassembles file and verifies checksum

### File Upload

1. Client reads local file and splits into chunks
2. Client sends each chunk to server
3. Server receives and stores chunks
4. Server acknowledges receipt of each chunk

## Configuration

The protocol can be configured for different network conditions:

```python
from protocol import ChunkSize, FileTransferProtocol

# For ultra-low bandwidth networks
protocol = FileTransferProtocol(
    chunk_size=ChunkSize.SMALL,     # 1 KB chunks
    compression=True                 # Enable compression
)

# For higher bandwidth
protocol = FileTransferProtocol(
    chunk_size=ChunkSize.XLARGE,    # 64 KB chunks
    compression=False                # Disable compression if not needed
)
```

## Performance Optimization

For optimal performance on low-bandwidth networks:

1. Use smaller chunk sizes (SMALL or MEDIUM)
2. Enable compression for text files
3. Disable compression for already-compressed files (JPG, ZIP, etc.)
4. Use appropriate timeout values
5. Implement retry logic for unreliable connections

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Check code quality
flake8 *.py
black *.py
pylint *.py
```

## Testing

To test the implementation:

```bash
# Terminal 1: Start the server
python server.py localhost 5000 ./test_files

# Terminal 2: Test file download
python client.py localhost 5000 download test_file.txt

# Terminal 3: Test file upload
python client.py localhost 5000 upload local_file.txt
```

## Future Enhancements

- [ ] Implement file resume capability
- [ ] Add bandwidth throttling
- [ ] Implement peer-to-peer mode
- [ ] Add authentication and encryption
- [ ] Implement directory transfer
- [ ] Add progress monitoring
- [ ] Create web UI
- [ ] Add metrics and logging

## License

This project is provided for educational purposes. Feel free to use and modify as needed.

## Educational Purpose

This project is designed as an educational tool to understand:

- Network socket programming
- Protocol design and implementation
- Data compression techniques
- Multi-threading and concurrent programming
- File I/O operations
- Error handling and recovery
- Low-bandwidth optimization strategies

## Support

For questions or issues, please open an issue on GitHub.

## Author

Created as an educational project demonstrating file sharing protocols for low-bandwidth networks.
