
import os
import json
import random
from PIL import Image, ImageDraw
from datetime import datetime

# Configuration
width, height = 640, 480
background_colors = {
    (255, 255, 255): 'white',
    (0, 0, 0): 'black',
    (255, 0, 0): 'red',
    (0, 255, 0): 'green',
    (0, 0, 255): 'blue',
    (255, 255, 0): 'yellow'
}
labels = ['deaddot', 'brightdot', 'discoloration', 'damage']
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# JSON Data Structure
images = []
annotations = []
categories = [{'id': i+1, 'name': label} for i, label in enumerate(labels)]

# Utility Function for Filename Generation
def generate_filename(defect_type, color_name):
    return f"{defect_type}_{color_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

# Function to Generate Images with Dots
def generate_images():
    image_id = 0
    annotation_id = 0

    for bg_color, color_name in background_colors.items():
        dot_color = (0, 0, 0) if bg_color != (0, 0, 0) else (255, 255, 255)  # Black for non-black backgrounds, white for black

        for x in range(width):
            for y in range(height):
                img = Image.new('RGB', (width, height), bg_color)
                draw = ImageDraw.Draw(img)

                # Draw the dot
                draw.point((x, y), fill=dot_color)

                # Save the image
                file_name = generate_filename('deaddot', color_name)
                img.save(os.path.join(output_dir, file_name))

                # Record the image and annotation
                images.append({'id': image_id, 'file_name': file_name, 'width': width, 'height': height})
                annotations.append({
                    'id': annotation_id, 'image_id': image_id, 'category_id': 1,
                    'bbox': [x, y, 1, 1], 'area': 1, 'iscrowd': 0
                })

                image_id += 1
                annotation_id += 1

# Save JSON Annotations
def save_annotations():
    annotation_data = {'images': images, 'annotations': annotations, 'categories': categories}
    with open(os.path.join(output_dir, 'coco.json'), 'w') as f:
        json.dump(annotation_data, f, indent=4)

# Main Execution
if __name__ == "__main__":
    generate_images()
    save_annotations()
