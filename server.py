"""Server implementation for Educational File Sharing Protocol

Provides server functionality for hosting files and handling protocol requests
from multiple clients using the low-bandwidth file sharing protocol.
"""

import socket
import os
import threading
from pathlib import Path
from typing import Optional, Dict
from protocol import FileTransferProtocol, ChunkSize, ProtocolMessage, MessageType


class FileShareServer:
    """Server for hosting files and handling file sharing requests."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, data_dir: str = "./shared_files"):
        """
        Initialize the file sharing server.

        Args:
            host: Server bind address (0.0.0.0 for all interfaces)
            port: Port to listen on
            data_dir: Directory to serve files from
        """
        self.host = host
        self.port = port
        self.data_dir = data_dir
        self.socket = None
        self.running = False
        self.protocol = FileTransferProtocol(chunk_size=ChunkSize.MEDIUM, compression=True)
        self.client_count = 0
        self.active_connections = {}

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def start(self):
        """Start the server and listen for incoming connections."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            print(f"Server listening on {self.host}:{self.port}")
            print(f"Serving files from: {os.path.abspath(self.data_dir)}")
            self._accept_connections()
        except Exception as e:
            print(f"Server error: {e}")
            self.running = False

    def stop(self):
        """Stop the server and close all connections."""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Server stopped")

    def _accept_connections(self):
        """Accept incoming client connections in a loop."""
        while self.running:
            try:
                client_socket, client_addr = self.socket.accept()
                self.client_count += 1
                client_id = self.client_count
                print(f"Client {client_id} connected from {client_addr}")
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id, client_addr),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")

    def _handle_client(self, client_socket: socket.socket, client_id: int, client_addr: tuple):
        """Handle individual client connection."""
        try:
            self.active_connections[client_id] = client_socket
            response = self._process_client_request(client_socket, client_id)
            if response:
                client_socket.sendall(response)
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected")

    def _process_client_request(self, client_socket: socket.socket, client_id: int) -> Optional[bytes]:
        """Process incoming client request."""
        try:
            data = client_socket.recv(1024)
            if not data:
                return None

            msg_type = data[0]
            if msg_type == MessageType.HANDSHAKE.value:
                return self._handle_handshake(client_socket, data)
            elif msg_type == MessageType.FILE_REQUEST.value:
                return self._handle_file_request(client_socket, data)
            elif msg_type == MessageType.CHUNK_DATA.value:
                return self._handle_chunk_upload(client_socket, data)
            else:
                error_msg = "Unknown message type".encode('utf-8')
                import struct
                return struct.pack('BBI', MessageType.ERROR.value, 1, len(error_msg)) + error_msg
        except Exception as e:
            print(f"Error processing request from client {client_id}: {e}")
            return None

    def _handle_handshake(self, client_socket: socket.socket, data: bytes) -> bytes:
        """Handle protocol handshake."""
        print("Handshake initiated")
        return ProtocolMessage.create_handshake(self.protocol.protocol_version)

    def _handle_file_request(self, client_socket: socket.socket, data: bytes) -> Optional[bytes]:
        """Handle file download request from client."""
        try:
            import struct
            filename_len = struct.unpack('I', data[1:5])[0]
            filename = data[5:5 + filename_len].decode('utf-8')
            filepath = os.path.join(self.data_dir, os.path.basename(filename))

            if os.path.exists(filepath) and os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                chunks = self.protocol.split_file(file_data)
                print(f"Sending file {filename} ({len(file_data)} bytes) in {len(chunks)} chunks")
                for i, chunk in enumerate(chunks):
                    msg = ProtocolMessage.create_chunk(i, chunk, self.protocol.compression)
                    client_socket.sendall(msg)
                return ProtocolMessage.create_message(MessageType.COMPLETE, b'')
            else:
                error_msg = f"File not found: {filename}".encode('utf-8')
                return struct.pack('BBI', MessageType.ERROR.value, 2, len(error_msg)) + error_msg
        except Exception as e:
            error_msg = str(e).encode('utf-8')
            import struct
            return struct.pack('BBI', MessageType.ERROR.value, 3, len(error_msg)) + error_msg

    def _handle_chunk_upload(self, client_socket: socket.socket, data: bytes) -> Optional[bytes]:
        """Handle file upload chunk from client."""
        try:
            chunk_index, payload, compressed = ProtocolMessage.parse_chunk(data)
            print(f"Received chunk {chunk_index} ({len(payload)} bytes, compressed={compressed})")
            import struct
            return struct.pack('BBI', MessageType.CHUNK_ACK.value, chunk_index, 0)
        except Exception as e:
            error_msg = str(e).encode('utf-8')
            import struct
            return struct.pack('BBI', MessageType.ERROR.value, 4, len(error_msg)) + error_msg

    def list_available_files(self) -> list:
        """Return list of available files in the data directory."""
        try:
            return os.listdir(self.data_dir)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


def main():
    """Main server entry point."""
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    data_dir = sys.argv[3] if len(sys.argv) > 3 else "./shared_files"

    server = FileShareServer(host=host, port=port, data_dir=data_dir)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()


if __name__ == "__main__":
    main()
