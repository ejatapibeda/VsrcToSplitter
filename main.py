from flask import Flask, request, jsonify
import requests
from urllib.parse import urljoin

app = Flask(__name__)

def split_m3u(m3u_content, base_url):
    resolutions = {
        '640x360': None,
        '854x480': None,
        '1280x720': None,
        '1920x1080': None,
        'auto': None  # Tambahkan auto di sini
    }

    lines = m3u_content.splitlines()
    current_resolution = None

    for line in lines:
        if line.startswith('#EXT-X-STREAM-INF:'):
            if 'RESOLUTION=' in line:
                current_resolution = line.split('RESOLUTION=')[1].split(',')[0]
            else:
                # Jika tidak ada resolusi yang tersedia, kita asumsikan sebagai 'auto'
                current_resolution = 'auto'
                
            # Untuk resolusi auto, kita tambahkan URL asli dari file M3U
            if current_resolution == 'auto':
                resolutions[current_resolution] = base_url
        elif current_resolution:
            resolutions[current_resolution] = urljoin(base_url, line)
            current_resolution = None

    return resolutions

@app.route('/split_m3u', methods=['POST'])
def split_m3u_endpoint():
    data = request.json
    m3u_url = data.get('m3u_url')
    
    if not m3u_url:
        return jsonify({'error': 'No m3u_url provided'}), 400

    response = requests.get(m3u_url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to download M3U file'}), 400

    m3u_content = response.text
    base_url = m3u_url.rsplit('/', 1)[0] + '/'
    resolutions = split_m3u(m3u_content, base_url)
    
    # Set auto resolution to the original M3U URL
    resolutions['auto'] = m3u_url
    
    return jsonify(resolutions)


if __name__ == '__main__':
    app.run(debug=True)
