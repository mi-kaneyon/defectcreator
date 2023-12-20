
import os
import json
from PIL import Image, ImageDraw
import random

def create_good_images(output_dir='ok', number_of_images=100):
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
    images = []
    annotations = []
    image_id = 0
    annotation_id = 0

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for color, color_name in background_colors.items():
        for i in range(number_of_images):
            image_name = f"{color_name}_{i+1}.png"
            image_path = os.path.join(output_dir, image_name)

            # Create an image with the specified background color
            img = Image.new('RGB', (width, height), color=color)
            img.save(image_path)

            # Add image and annotation info to JSON data
            images.append({
                "file_name": image_name,
                "height": height,
                "width": width,
                "id": image_id
            })
            annotations.append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 1,  # Assuming a single category for good images
                "bbox": [0, 0, width, height],
                "area": width * height,
                "iscrowd": 0
            })

            image_id += 1
            annotation_id += 1

    # Save the COCO JSON data
    coco_json = {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "good"}]
    }
    with open(os.path.join(output_dir, 'coco_annotations.json'), 'w') as f:
        json.dump(coco_json, f, indent=4)

    return f"Generated {number_of_images * len(background_colors)} good images in {output_dir}."

# Run the function to create good images
create_good_images()
    
