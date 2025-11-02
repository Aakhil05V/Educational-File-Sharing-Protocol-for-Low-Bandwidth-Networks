"""Client implementation for Educational File Sharing Protocol

Provides client functionality for downloading and uploading files
using the low-bandwidth file sharing protocol.
"""

import socket
import os
import sys
from pathlib import Path
from typing import Optional
from protocol import FileTransferProtocol, ChunkSize, ProtocolMessage, MessageType


class FileShareClient:
    """Client for connecting to file sharing server."""

    def __init__(self, host: str, port: int, chunk_size: ChunkSize = ChunkSize.MEDIUM):
        """
        Initialize the client.

        Args:
            host: Server hostname or IP address
            port: Server port number
            chunk_size: Size of chunks for file transfer
        """
        self.host = host
        self.port = port
        self.socket = None
        self.protocol = FileTransferProtocol(chunk_size=chunk_size, compression=True)
        self.connected = False

    def connect(self) -> bool:
        """Establish connection to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            return self._handshake()
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Close connection to server."""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("Disconnected from server")

    def _handshake(self) -> bool:
        """Perform protocol handshake with server."""
        try:
            handshake_msg = ProtocolMessage.create_handshake(self.protocol.protocol_version)
            self.socket.sendall(handshake_msg)
            response = self.socket.recv(1024)
            return len(response) > 0
        except Exception as e:
            print(f"Handshake failed: {e}")
            return False

    def download_file(self, remote_filename: str, local_path: Optional[str] = None) -> bool:
        """
        Download a file from server.

        Args:
            remote_filename: Name of file to download from server
            local_path: Local path to save file (defaults to remote_filename)
        """
        if not self.connected:
            print("Not connected to server")
            return False

        if local_path is None:
            local_path = remote_filename

        try:
            print(f"Downloading {remote_filename} to {local_path}...")
            request = self._create_file_request(remote_filename)
            self.socket.sendall(request)
            return self._receive_file(local_path)
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def upload_file(self, local_path: str, remote_filename: Optional[str] = None) -> bool:
        """
        Upload a file to server.

        Args:
            local_path: Path to local file
            remote_filename: Name to save on server (defaults to basename of local_path)
        """
        if not self.connected:
            print("Not connected to server")
            return False

        if not os.path.exists(local_path):
            print(f"File not found: {local_path}")
            return False

        if remote_filename is None:
            remote_filename = os.path.basename(local_path)

        try:
            print(f"Uploading {local_path} as {remote_filename}...")
            with open(local_path, 'rb') as f:
                file_data = f.read()
            return self._send_file(remote_filename, file_data)
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def _send_file(self, filename: str, file_data: bytes) -> bool:
        """Send file data to server in chunks."""
        chunks = self.protocol.split_file(file_data)
        checksum = self.protocol.calculate_checksum(file_data)
        total_chunks = len(chunks)

        print(f"Sending {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            try:
                msg = ProtocolMessage.create_chunk(i, chunk, self.protocol.compression)
                self.socket.sendall(msg)
                if (i + 1) % 10 == 0:
                    print(f"Sent {i + 1}/{total_chunks} chunks")
            except Exception as e:
                print(f"Error sending chunk {i}: {e}")
                return False

        print("File upload complete")
        return True

    def _receive_file(self, output_path: str) -> bool:
        """Receive file data from server in chunks."""
        chunks = []
        try:
            while True:
                try:
                    data = self.socket.recv(65536)
                    if not data:
                        break
                    chunks.append(data)
                except socket.timeout:
                    break

            if chunks:
                file_data = b''.join(chunks)
                with open(output_path, 'wb') as f:
                    f.write(file_data)
                print(f"File downloaded successfully to {output_path}")
                return True
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False

        return False

    def _create_file_request(self, filename: str) -> bytes:
        """Create file request message."""
        msg_type = MessageType.FILE_REQUEST.value
        filename_bytes = filename.encode('utf-8')
        import struct
        return struct.pack('BI', msg_type, len(filename_bytes)) + filename_bytes

    def list_files(self) -> bool:
        """Request list of available files from server."""
        if not self.connected:
            print("Not connected to server")
            return False
        print("Requesting file list...")
        return True


def main():
    """Main client entry point."""
    if len(sys.argv) < 2:
        print("Usage: python client.py <host> <port> [download|upload] [filename]")
        return

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    client = FileShareClient(host, port)
    if client.connect():
        if len(sys.argv) > 3 and sys.argv[3] == "download" and len(sys.argv) > 4:
            client.download_file(sys.argv[4])
        elif len(sys.argv) > 3 and sys.argv[3] == "upload" and len(sys.argv) > 4:
            client.upload_file(sys.argv[4])
        client.disconnect()


if __name__ == "__main__":
    main()
