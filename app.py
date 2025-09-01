#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 14:27:51 2024

@author: yashbagia
"""

# app.py
import os
import requests
from hashlib import sha1
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, send_file, send_from_directory
from flask_socketio import SocketIO, emit
from urllib.parse import urlparse
import zipfile
from werkzeug.utils import safe_join
from threading import Thread
from queue import Queue
from analyze import trigger_analysis, analyze_images, clear_sorted_images
import ssl
import certifi
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

FIGMA_TOKEN = os.environ.get('FIGMA_TOKEN', 'figd_CLMBA9f8XlW_LCN0druO3FX-clz4jJ6OOKB3l9oo')
BASE_FOLDER_PATH = "static/output_images/"
os.makedirs(BASE_FOLDER_PATH, exist_ok=True)
image_count = 0

mobile_min_width, mobile_max_width = 0, 480
tablet_min_width, tablet_max_width = 481, 1024
pc_min_width, pc_max_width = 1025, float('inf')

mobile_min_height, mobile_max_height = 480, 896
tablet_min_height, tablet_max_height = 900, 1366
pc_min_height, pc_max_height = 768, float('inf')

extraction_status = {"completed": False, "error": None}
analysis_status = {"completed": False, "error": None}

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename):
    return filename.replace('/', '_').replace('\\', '_')

def clear_output_images():
    if os.path.exists(BASE_FOLDER_PATH):
        for filename in os.listdir(BASE_FOLDER_PATH):
            file_path = os.path.join(BASE_FOLDER_PATH, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

def get_image_url(file_key, node_id):
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}"
    headers = {'X-Figma-Token': FIGMA_TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["images"].get(node_id)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image URL for node {node_id}: {e}")
        socketio.emit('update', {'message': f"Error fetching image URL for node {node_id}: {e}"})
        return None

def download_image(image_url, file_name):
    global image_count
    if not image_url:
        print(f"Invalid image URL: {image_url}")
        socketio.emit('update', {'message': f"Invalid image URL: {image_url}"})
        return False
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image to {file_name}")
        socketio.emit('update', {'message': f"Downloaded image to {file_name}"})
        image_count += 1
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
        socketio.emit('update', {'message': f"Error downloading image from {image_url}: {e}"})
        return False

def find_top_level_frames(document):
    frames_info = []
    excluded_types = ["SECTION", "INSTANCE"]

    def traverse(node):
        if node["type"] == "CANVAS":
            for child in node.get("children", []):
                if child["type"] not in excluded_types:
                    frame_width = child["absoluteBoundingBox"]["width"]
                    frame_height = child["absoluteBoundingBox"]["height"]
                    if (mobile_min_width <= frame_width <= pc_max_width) and (
                            mobile_min_height <= frame_height <= pc_max_height):
                        if frame_height > 700:
                            frames_info.append((child["id"], child.get("name", ""), child))
                        else:
                            print(f"Skipped frame {child.get('name', '')} due to insufficient height")
                            socketio.emit('update', {'message': f"Skipped frame {child.get('name', '')} due to insufficient height"})
        for child in node.get("children", []):
            traverse(child)

    traverse(document)
    return frames_info

def reset_extraction_status():
    global extraction_status
    global analysis_status
    extraction_status = {"completed": False, "error": None}
    analysis_status = {"completed": False, "error": None}

def extract_images(file_key, result_queue):
    global extraction_status
    global analysis_status
    try:
        headers = {'X-Figma-Token': FIGMA_TOKEN}
        response = requests.get(f'https://api.figma.com/v1/files/{file_key}', headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        frame_info = find_top_level_frames(data["document"])

        if not frame_info:
            extraction_status["error"] = "No frames found in the Figma file."
            result_queue.put({'status': 'error', 'message': 'No frames found in the Figma file.'})
            socketio.emit('update', {'message': 'No frames found in the Figma file.'})
            return

        for frame_id, frame_name, frame_data in frame_info:
            image_url = get_image_url(file_key, frame_id)
            if image_url:
                frame_width = frame_data["absoluteBoundingBox"]["width"]
                frame_height = frame_data["absoluteBoundingBox"]["height"]
                category_folder_path = os.path.join(BASE_FOLDER_PATH)
                os.makedirs(category_folder_path, exist_ok=True)
                sanitized_frame_name = sanitize_filename(frame_name)
                hash_name = sha1(frame_id.encode()).hexdigest()[:8]
                image_file_name = os.path.join(category_folder_path, f"{sanitized_frame_name}_{image_count}.png")
                if not download_image(image_url, image_file_name):
                    print(f"Unable to download image for frame {frame_name} ({frame_id})")
                    socketio.emit('update', {'message': f"Unable to download image for frame {frame_name} ({frame_id})"})
            else:
                print(f"No image URL found for frame {frame_name} ({frame_id})")
                socketio.emit('update', {'message': f"No image URL found for frame {frame_name} ({frame_id})"})

        extraction_status["completed"] = True
        result_queue.put({'status': 'success'})

        # Trigger analysis after extraction
        clear_sorted_images()
        analyze_images('static/output_images', 'static/sorted_images')
        analysis_status["completed"] = True
        
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        extraction_status["error"] = str(e)
        result_queue.put({'status': 'error',
                          'message': 'An error occurred while trying to reach the Figma file. Please check the link or try again later.'})
        socketio.emit('update', {'message': f"RequestException: {e}"})
    except Exception as e:
        print(f"Exception: {e}")
        extraction_status["error"] = str(e)
        result_queue.put({'status': 'error', 'message': 'An unexpected error occurred. Please try again later.'})
        socketio.emit('update', {'message': f"Exception: {e}"})

@app.route('/')
def index():
    clear_output_images()
    title = "Zippy"
    message = "Image extraction from Figma file."
    return render_template('index.html', title=title, message=message)

@app.route('/display')
def display():
    title = "Display:"
    return render_template('display.html', title=title, images=os.listdir(BASE_FOLDER_PATH))

@app.route('/loading')
def loading():
    title = "Loading...Please wait...."
    message = "Extracting Screens.."
    return render_template('loading.html', title=title, message=message)

@app.route('/errorpage')
def errorpage():
    title = "404 error:("
    return render_template('errorPage.html', title=title)

@app.route('/variationDisplay')
def variationDisplay():
   title =  "Display:"
   return render_template('variationDisplay.html', title = title, images=os.listdir(BASE_FOLDER_PATH))

@app.route('/check-url', methods=['POST'])
def check_url():
    url = request.form.get('url')
    if not url:
        abort(400, 'No URL provided')

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        if response.status_code >= 200 and response.status_code < 300:
            return jsonify({'status': 'success', 'message': 'URL is accessible'})
        else:
            abort(response.status_code, 'URL is not accessible or does not exist')
    except requests.exceptions.RequestException as e:
        abort(500, str(e))

@app.route('/check-images-count')
def check_images_count():
    images = [img for img in os.listdir(BASE_FOLDER_PATH) if img.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return jsonify({'images': images, 'imagesCount': image_count})

@app.route('/download-zip')
def download_zip():
    selected_images = request.args.get('selected', '').split(';')
    screen_indices = request.args.get('indices', '').split(';')

    if not selected_images:
        return abort(400, 'No images selected')

    zip_filename = 'screens_and_variations.zip'
    zip_filepath = os.path.join(BASE_FOLDER_PATH, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        screen_folder = 'screens'
        variation_folder = 'variations'

        for image, index in zip(selected_images, screen_indices):
            screen_path = os.path.join(BASE_FOLDER_PATH, image)
            variation_path = os.path.join('static', 'sorted_images', f'screen_{index}', 'above_70')

            if os.path.exists(screen_path):
                zipf.write(screen_path, os.path.join(screen_folder, os.path.basename(screen_path)))

            if os.path.exists(variation_path):
                for variation in os.listdir(variation_path):
                    full_variation_path = os.path.join(variation_path, variation)
                    zipf.write(full_variation_path, os.path.join(variation_folder, f"{os.path.basename(screen_path).split('.')[0]}_{variation}"))

    return send_file(zip_filepath, as_attachment=True)

@app.route('/check-extraction-status')
def check_extraction_status():
    global extraction_status
    global analysis_status
    return jsonify({"extraction": extraction_status, "analysis": analysis_status})

@app.route('/get-variations/<int:screen_index>')
def get_variations(screen_index):
    variations_path = os.path.join('static', 'sorted_images', f'screen_{screen_index}', 'above_70')
    if not os.path.exists(variations_path):
        return jsonify({'status': 'error', 'message': 'No variations found'}), 404

    variations = [url_for('static', filename=f'sorted_images/screen_{screen_index}/above_70/{img}')
                  for img in os.listdir(variations_path) if img.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]

    return jsonify({'status': 'success', 'images': variations})

@app.route('/extract', methods=['POST'])
def extract():
    global image_count
    url = request.form['inputUrl']
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    if len(path_segments) < 3 or path_segments[1] != "design":
        return jsonify({'status': 'error', 'message': 'Invalid Figma URL.'})

    file_key = path_segments[2]
    result_queue = Queue()
    reset_extraction_status()
    image_count = 0
    thread = Thread(target=extract_images, args=(file_key, result_queue))
    thread.start()
    return redirect(url_for('loading'))

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
