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
- See `requirements.txt` for Python dependencies

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Educational-File-Sharing-Protocol-for-Low-Bandwidth-Networks
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Socket-Based Protocol

1. Start the server:
   ```bash
   python server.py
   ```

2. In another terminal, run the client:
   ```bash
   python client.py
   ```

### Web Usage

A modern web interface is available for easy file management without using the command line.

1. Start the Flask web server:
   ```bash
   python web_server.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. The web interface provides:
   - **File Upload**: Upload files via drag-and-drop or file picker
   - **File Download**: Download files directly from the browser
   - **File List**: View all available files with their details
   - **Responsive UI**: Works on desktop and mobile devices

#### Web Interface Features

- **User-Friendly Dashboard**: Simple and intuitive interface for file operations
- **Real-time Status**: Get immediate feedback on upload/download operations
- **File Management**: View file sizes and upload timestamps
- **Error Handling**: Clear error messages for troubleshooting

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Future Enhancements

- [ ] Create web UI ✓ (Completed)
- [ ] Implement streaming for large files
- [ ] Add authentication and authorization
- [ ] Support for cloud storage backends
- [ ] Performance monitoring and analytics
- [ ] Mobile app for iOS and Android

## License

This project is open source and available under the MIT License.
