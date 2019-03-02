"""Preprocess the Centaur model

The model is available for download from
    https://sketchfab.com/models/0d3f1b4a51144b7fbc4e2ff64d858413

The Python Imaging Library is required
    pip install pillow
"""

from __future__ import print_function

import json
import os
import zipfile
from PIL import Image
from utils.gltf import dump_obj_data

SRC_FILENAME = "centaur.zip"
DST_DIRECTORY = "../assets/centaur"

OBJ_FILENAMES = [
    "body.obj",
    None,
    "flame.obj",
    "gas.obj",
]

IMG_FILENAMES = {
    # body textures
    "textures/body_diffuse.jpeg": "body_diffuse.tga",
    "textures/body_emissive.jpeg": "body_emission.tga",
    "textures/body_specularGlossiness.png": "body_specular.tga",
    # flame textures
    "textures/flame_diffuse.png": "flame_diffuse.tga",
    "textures/flame_emissive.jpeg": "flame_emission.tga",
    # gas textures
    "textures/material_diffuse.jpeg": "gas_diffuse.tga",
    "textures/material_specularGlossiness.png": "gas_specular.tga",
}


def fix_flame_data(flame_data):
    start = flame_data.find("f 1/1/1 2/2/2 3/3/3")
    end = flame_data.find("f 458/458/458 459/459/459 460/460/460")
    return flame_data[:start] + flame_data[end:]


def process_meshes(zip_file):
    gltf = json.loads(zip_file.read("scene.gltf"))
    buffer = zip_file.read("scene.bin")

    for mesh_index, filename in enumerate(OBJ_FILENAMES):
        if filename:
            obj_data = dump_obj_data(gltf, buffer, mesh_index)
            if mesh_index == 2:
                obj_data = fix_flame_data(obj_data)
            filepath = os.path.join(DST_DIRECTORY, filename)
            with open(filepath, "w") as f:
                f.write(obj_data)


def linear_to_srgb(image):
    lookup_table = [pow(x / 255.0, 1 / 2.2) * 255 for x in range(256)] * 3
    return image.point(lookup_table)


def process_images(zip_file):
    for old_filename, tga_filename in IMG_FILENAMES.items():
        with zip_file.open(old_filename) as f:
            image = Image.open(f)
            if "specularGlossiness" in old_filename:
                image = linear_to_srgb(image)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image = image.resize((512, 512), Image.LANCZOS)
            filepath = os.path.join(DST_DIRECTORY, tga_filename)
            image.save(filepath, rle=True)


def main():
    if not os.path.exists(DST_DIRECTORY):
        os.makedirs(DST_DIRECTORY)

    with zipfile.ZipFile(SRC_FILENAME) as zip_file:
        process_meshes(zip_file)
        process_images(zip_file)


if __name__ == "__main__":
    main()
