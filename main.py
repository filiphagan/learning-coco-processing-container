#!/usr/bin/env python

"""
Main.py: downloads zipped COCO dataset, preprocesses the data into pandas dataframes
and exports merged dataframe into CSV
"""

__author__ = "Filip Hagan"

import os
import sys
import time
import json
import logging
import zipfile
import urllib.request
import pandas as pd

from typing import Tuple
from urllib.error import URLError, HTTPError
from argparse import ArgumentParser, Namespace

# Logging settings. Logs are being saved in ./api.log
logging.basicConfig(filename="api.log")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info(f"Run started at {time.asctime()}")


def parse_args() -> Namespace:
    """Returns argparse.Namespace with parsed parameters"""

    # Parsed parameters
    parser = ArgumentParser()
    parser.add_argument("--url",
                        default="http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
                        type=str)
    parser.add_argument("--output", default="output.csv", type=str)

    params = parser.parse_args()

    return params


def get_parse_data(url_data_zip: str) -> dict:
    """Given URL to the zipped dataset returns parsed content of person_keypoints_val2017.json

    Parameters
    ----------
    url_data_zip : str
        By default expecting 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip'

    Returns
    ----------
    result : dict
        Data of person_keypoints_val2017.json parsed to dictionary
    """
    try:
        zip_file, _ = urllib.request.urlretrieve(url_data_zip, "data.zip")
    except (HTTPError, URLError) as er:
        logger.error(f"{time.asctime()}: Connection error. {er}")
        raise er

    zip_file_obj = zipfile.ZipFile(zip_file, 'r')

    if "annotations/person_keypoints_val2017.json" not in zip_file_obj.namelist():
        er = f"{time.asctime()}: Missing person_keypoints_val2017.json in zip file"
        logger.error(er)
        raise AssertionError(er)

    json_file = zip_file_obj.open("annotations/person_keypoints_val2017.json")
    data_dict = json.load(json_file)

    if set(data_dict.keys()) != {'info', 'licenses', 'images', 'annotations', 'categories'}:
        er = f"{time.asctime()}: Data keys don't match. Aborting operation."
        logger.error(er)
        raise AssertionError(er)

    return data_dict


def create_dataframes(data: dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns 3 COCO pandas dataframes 'categories', 'images', 'annotations'

    Parameters
    ----------
    data : dict
        Dictionary including all the data from parsed json 'person_keypoints_val2017'

    Returns
    ----------
    categories, images, annotations : tuple (pandas dataframes)
        Processed and filtered dataframes
    """
    # Build categories dataframe
    cat_filter = ["id", "name"]
    cat_filtered = [{key: d[key] for key in cat_filter} for d in data["categories"]]
    cat_df = pd.DataFrame(cat_filtered)
    cat_df.rename(columns={"name": "label", "id": "category_id"}, inplace=True)

    # Build images dataframe
    img_filter = ["file_name", "coco_url", "height", "width", "id"]
    img_df = pd.DataFrame(data["images"])
    img_df = img_df[img_filter]
    img_df.rename(columns={
        "id": "image_id",
        "file_name": "image_name",
        "height": "image_height",
        "width": "image_width",
        "coco_url": "image_url"},
        inplace=True)

    # Build annotations dataframe
    annotations = []
    for obj in data["annotations"]:
        row = {}

        try:
            row["image_id"] = obj["image_id"]
            row["category_id"] = obj["category_id"]

            # Bounding box [x,y,width,height] where x, y represents top left corner
            x_min, y_min, width, height = obj["bbox"]

        except (ValueError, KeyError) as e:
            logger.error(f"{time.asctime()}: Unable to process annotation data. Error: {e}")
            raise e

        row["x_min"] = x_min
        row["y_min"] = y_min
        row["x_max"] = round(x_min + width, 2)
        row["y_max"] = round(y_min + height, 2)

        annotations.append(row)
    anno_df = pd.DataFrame(annotations)

    return cat_df, img_df, anno_df


def save_csv(dataframe: pd.DataFrame, path: str) -> None:
    """Saves dataframe to given directory

    Parameters
    ----------
    dataframe : pandas dataframe
    path : str
        Path to output file including filename
    """
    directory = os.path.dirname(path)
    # Checking if directory exist, creating missing directory
    if not os.path.isdir(directory):
        os.mkdir(directory)

    dataframe.to_csv(path, index=False)
    logger.info(f"File saved in {path}")


if __name__ == "__main__":

    # Parse parameters
    args = parse_args()
    url = args.url
    output_path = args.output

    cols = ["label", "image_name", "image_width", "image_height",
            "x_min", "y_min", "x_max", "y_max", "image_url"]

    # Download and parse the data
    dict_data = get_parse_data(url)

    if not dict_data:
        logger.info(f"{time.asctime()}: Unable to parse the data")
        raise ValueError("Empty dictionary")

    # Create pandas dataframes
    categories_df, images_df, annotations_df = create_dataframes(dict_data)

    # Join images_df
    final_df = annotations_df.merge(images_df, how="left", left_on="image_id", right_on="image_id")
    # Join categories_df
    final_df = final_df.merge(categories_df, how="left", left_on="category_id", right_on="category_id")
    # Select necessary columns in proper order
    final_df = final_df[cols]
    logger.info(f"Dataframe created")

    # Save dataframe
    save_csv(final_df, output_path)
    logger.info(f"Run ended at {time.asctime()}")
