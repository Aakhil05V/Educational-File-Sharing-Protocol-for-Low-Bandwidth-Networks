from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import mimetypes

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['UPLOAD_FOLDER'] = 'shared_files'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Create shared_files directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7z', 'tar', 'gz', 'mp4', 'mkv', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main web interface"""
    return render_template('index.html')

@app.route('/files', methods=['GET'])
def list_files():
    """List all available files in shared_files directory"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                files.append({
                    'filename': filename,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        return jsonify({'files': files, 'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads with chunking support"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Handle file chunks if provided
        chunk = request.form.get('chunk', 0, type=int)
        chunks = request.form.get('chunks', 1, type=int)
        
        file.save(filepath)
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': os.path.getsize(filepath)
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download file from shared_files with chunked response support"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        if not os.path.isfile(filepath):
            return jsonify({'status': 'error', 'message': 'Invalid file path'}), 400
        
        # Get file size for response headers
        file_size = os.path.getsize(filepath)
        
        # Support for Range requests (chunked downloads)
        range_header = request.headers.get('Range')
        if range_header:
            return send_file_range(filepath, range_header)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_file_range(filepath, range_header):
    """Handle HTTP Range requests for chunked downloads"""
    file_size = os.path.getsize(filepath)
    
    try:
        range_parts = range_header.replace('bytes=', '').split('-')
        start = int(range_parts[0]) if range_parts[0] else 0
        end = int(range_parts[1]) if range_parts[1] else file_size - 1
        
        if start > end or start >= file_size:
            return 'Invalid range', 416
        
        chunk_size = min(end - start + 1, 1024 * 1024)  # 1MB chunks
        
        with open(filepath, 'rb') as f:
            f.seek(start)
            content = f.read(chunk_size)
        
        response = app.response_class(
            response=content,
            status=206,
            mimetype=mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        )
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.headers['Content-Length'] = len(content)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from shared_files"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        if not os.path.isfile(filepath):
            return jsonify({'status': 'error', 'message': 'Invalid file path'}), 400
        
        os.remove(filepath)
        return jsonify({'status': 'success', 'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'status': 'error', 'message': 'File too large (max 500MB)'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

if __name__ == '__main__':
    import sys
    
    # Parse command-line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    debug = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    print(f"Starting Flask File Sharing Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Access the web interface at http://{host}:{port}/")
    
    app.run(host=host, port=port, debug=debug)
