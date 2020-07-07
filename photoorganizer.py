from PIL import Image
from PIL import ImageFile

import datetime
import imagehash
import math
import logging
import os
import PIL
import shutil
import sys
import time

# Constants
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
SUPPORTED_VIDEO_EXTENSIONS = {".mov", ".mp4", ".mpeg", ".mpg", ".avi"}

# Setup the logger.
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(os.path.splitext(sys.argv[0])[0] + ".log")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s"))
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
console_handler.setLevel(logging.INFO)
root_logger.addHandler(console_handler)


# Handles image files that are slightly corrupt but can still be read.
ImageFile.LOAD_TRUNCATED_IMAGES = True


def main():
    logging.debug("Arguments %s.", sys.argv)

    # Parse the arguments.
    mode = None
    file_name_lower = sys.argv[0].lower()
    if "monthly" in file_name_lower:
        mode = "monthly"
    elif "yearly" in file_name_lower:
        mode = "yearly"
    else:
        mode = "weekly"

    input_directory = None
    if len(sys.argv) == 1:
        print("Drag the photos folder here and press Enter/Return.")
        input_directory = input().strip()
    elif len(sys.argv) == 2:
        input_directory = sys.argv[1]
    elif len(sys.argv) > 2:
        raise ValueError("Exactly 1 argument for the input directory must be procided, instead got %d" % (len(sys.argv)-1))

    # Check if input_directory is a directory.
    if not os.path.isdir(input_directory):
        logging.info("Input must be a directory.")
    logging.info("Processing input directory %s." % input_directory)

    # Make the output directory.
    output_directory = input_directory + "-organized"
    logging.info("Making output directory %s." % output_directory)
    os.makedirs(output_directory, exist_ok=True)

    # Set of seen image hashes.
    seen_image_hashes = set()

    # Walk the input directory to find each JPG.
    for dir_name, _, file_list in os.walk(input_directory):
        logging.info("Found directory: %s" % dir_name)

        for file_name in file_list:
            input_file_path = os.path.join(dir_name, file_name)
            logging.info("Processing file: %s" % input_file_path)
            output_file_path = process(input_file_path, output_directory, mode, seen_image_hashes)
            copy(input_file_path, output_file_path)


def process(input_file_path, output_directory_path, mode, seen_file_hashes):
    '''
    Procesess the the input file path and returns where to output it
    '''
    input_file_name = os.path.basename(input_file_path)

    # Only process jpgs. Move the rest into an unknown folder.
    if not is_image(input_file_name) and not is_video(input_file_name):
        return os.path.join(output_directory_path, "unknown",  input_file_name)

    file_hash = None
    timestamp = None
    if is_image(input_file_name):
        logging.debug("Processing %s as image." % input_file_name)
        # Open the image.
        image = None
        try:
            image = Image.open(input_file_path)
        except BaseException:
            logging.debug("Error while opening image %s." % input_file_name, exc_info=True)
            return os.path.join(output_directory_path, "broken",  input_file_name)

        # Get the image taken datetime. If none, fallback to last modified.
        timestamp = get_taken_datetime(image)
        if timestamp is None:
            logging.debug("Image %s missing taken datetime. Falling back to modified timestamp." % input_file_name)
            timestamp = get_last_modified_datetime(input_file_path)

        # Get the image hash
        file_hash = imagehash.average_hash(image)

    if is_video(input_file_name):
        logging.debug("Processing %s as video." % input_file_name)
        # Get the last modified time for the video.
        timestamp = get_last_modified_datetime(input_file_path)

        # Use the input file path as the hash, as we dont have a good video hash algorithm.
        file_hash = input_file_path

    # Make the directory from the timestamp.
    timestamp_directory = None
    if mode == "yearly":
        timestamp_directory = os.path.join(output_directory_path, str(timestamp.year))
    elif mode == "monthly":
        timestamp_directory = os.path.join(output_directory_path, str(timestamp.year), str(timestamp.month).zfill(2))
    else:
        timestamp_week = math.floor(timestamp.day / 7) + 1
        timestamp_directory = os.path.join(output_directory_path, str(timestamp.year), str(timestamp.month).zfill(2), "Week " + str(timestamp_week).zfill(2))

    # Check for duplicates.
    if file_hash in seen_file_hashes:
        return os.path.join(timestamp_directory, "duplicates", input_file_name)

    # If we are here, the image is the first.
    seen_file_hashes.add(file_hash)
    return os.path.join(timestamp_directory, input_file_name)


def is_image(file_name):
    extension = os.path.splitext(file_name.lower())[1]
    return extension in SUPPORTED_IMAGE_EXTENSIONS


def is_video(file_name):
    extension = os.path.splitext(file_name.lower())[1]
    return extension in SUPPORTED_VIDEO_EXTENSIONS


def get_taken_datetime(image):
    try:
        metadata = image._getexif()
        if metadata is not None:
            taken_datetime_string = metadata[36867]
            return datetime.datetime.strptime(taken_datetime_string, "%Y:%m:%d %H:%M:%S")
    except:
        pass
    return None


def get_last_modified_datetime(file_path):
    modified_time_epoch = os.path.getmtime(file_path)
    return datetime.datetime.utcfromtimestamp(modified_time_epoch)


def copy(source, destination):
    destination_directory = os.path.dirname(destination)
    os.makedirs(destination_directory, exist_ok=True)

    final_destination = destination
    index = 0
    while os.path.exists(final_destination):
        index += 1
        base_name = os.path.basename(destination)
        file_name, ext = os.path.splitext(base_name)
        final_destination = os.path.join(destination_directory, file_name + "-" + "{:04}".format(index) + ext)

    logging.debug("Copying %s to %s." % (source, final_destination))
    shutil.copy2(source, final_destination)


if __name__ == "__main__":
    try:
        logging.info("Started processing.")
        start = datetime.datetime.now()
        main()
        end = datetime.datetime.now()
        logging.info("Finished processing. Took %s.", end-start)
    except BaseException:
        logging.error("Exception while processing.", exc_info=True)
    finally:
        time.sleep(5)
