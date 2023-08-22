import csv
import glob
import os
from collections import defaultdict
from urllib.parse import unquote, urlparse

import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import (
    dir_exists,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive

# https://www.kaggle.com/datasets/sovitrath/road-pothole-images-for-pothole-detection
# https://drive.google.com/drive/folders/1vUmCvdW3-2lMrhsMbXdMWeLcEz__Ocuy (ds1, ds2 used)


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)
        fsize = get_file_size(local_path)
        with tqdm(desc=f"Downloading '{file_name_with_ext}' to buffer..", total=fsize) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = get_file_size(local_path)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer {local_path}...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "Road Pothole detection"

    ds1_path_train = "APP_DATA/Dataset 1 (Simplex)/Train data"
    ds2_path_train = "APP_DATA/Dataset 2 (Complex)/Train data"

    ds1_path_test = "APP_DATA/Dataset 1 (Simplex)/Test data"
    ds2_path_test = "APP_DATA/Dataset 2 (Complex)/Test data"

    ds1_test_boxes_path = (
        "APP_DATA/Dataset 1 (Simplex)/simpleTestFullSizeAllPotholesSortedFullAnnotation.txt"
    )
    ds1_train_boxes_path = (
        "APP_DATA/Dataset 1 (Simplex)/simpleTrainFullPhotosSortedFullAnnotations.txt"
    )

    ds2_test_boxes_path = "APP_DATA/Dataset 2 (Complex)/complexTestFullSizeAllPotholes.txt"
    ds2_train_boxes_path = "APP_DATA/Dataset 2 (Complex)/complexTrainFullSizeAllPotholes.txt"

    ds_name_to_data = {
        "ds1_simplex-train": {
            "dataset1": (ds1_path_train, ds1_train_boxes_path),
        },
        "ds2_complex-train": {
            "dataset2": (ds2_path_train, ds2_train_boxes_path),
        },
        "ds1_simplex-test": {
            "dataset1": (ds1_path_test, ds1_test_boxes_path),
        },
        "ds2_complex-test": {
            "dataset2": (ds2_path_test, ds2_test_boxes_path),
        },
    }

    batch_size = 30
    img_height = 2760
    img_wight = 3680

    def create_ann(image_path):
        labels = []
        tags = []
        tag_names_ = []

        file_name = get_file_name(image_path)

        image_data = name_to_data.get(file_name)
        if image_data is not None:
            number_pothole_value = len(image_data)
            number_pothole = sly.Tag(tag_number_pothole, value=number_pothole_value)
            tags.append(number_pothole)
            for curr_image_data in image_data:
                bboxes = list(map(int, curr_image_data))

                left = bboxes[0]
                top = bboxes[1]
                right = bboxes[0] + bboxes[2]
                bottom = bboxes[1] + bboxes[3]
                rect = sly.Rectangle(left=left, top=top, right=right, bottom=bottom)
                label = sly.Label(rect, obj_class)
                labels.append(label)

        # ds_tag = sly.Tag(tag_ds, value=ds_tag_value)/
        # tags.append(ds_tag)
        # tag_names_.append(ds_tag_value)
        if ds_name == "train":
            if "Negative" in image_path:
                tag_names_.append("negative data")
            elif "Positive" in image_path:
                tag_names_.append("positive data")
            # type_tag = sly.Tag(tag_data_type, value=type_value)
            # tags.append(type_tag)

        tags += [sly.Tag(tag_meta) for tag_meta in tag_metas if tag_meta.name in tag_names_]
        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    obj_class = sly.ObjClass("pothole", sly.Rectangle)
    # tag_ds = sly.TagMeta("dataset", sly.TagValueType.ONEOF_STRING, possible_values=["1", "2"])
    # tag_data_type = sly.TagMeta(
    #     "data type",
    #     sly.TagValueType.ONEOF_STRING,
    #     possible_values=["Negative data", "Positive data"],
    # )
    tag_names = [
        "Negative data",
        "Positive data",
        # "Dataset 1 (Simplex)",
        # "Dataset 2 (Complex)",
    ]
    tag_metas = [sly.TagMeta(name, sly.TagValueType.NONE) for name in tag_names]

    tag_number_pothole = sly.TagMeta("pothole numbers", sly.TagValueType.ANY_NUMBER)

    # ds_to_tag = {"dataset1": "Dataset 1 (Simplex)", "dataset2": "Dataset 2 (Complex)"}

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[obj_class], tag_metas=tag_metas + [tag_number_pothole])
    api.project.update_meta(project.id, meta.to_json())

    for ds_name in list(ds_name_to_data.keys()):
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)
        if "train" in ds_name:
            name_index = 2
        else:
            name_index = 1
        ds_data = ds_name_to_data[ds_name]

        for sub_ds in list(ds_data.keys()):
            # ds_tag_value = ds_to_tag[sub_ds]
            images_folder = ds_data[sub_ds][0]
            boxes_path = ds_data[sub_ds][1]

            if "train" in ds_name:
                images_pathes = glob.glob(images_folder + "/*/*.JPG")
            else:
                images_pathes = [
                    os.path.join(images_folder, im_name) for im_name in os.listdir(images_folder)
                ]

            name_to_data = defaultdict(list)

            with open(boxes_path, "r") as f:
                content = f.read().split("\n")
                for row in content:
                    if len(row) == 0:
                        continue
                    data = row.strip().split(" ")
                    im_name = get_file_name(data[name_index].split("\\")[1])
                    boxes = data[name_index + 2 :]
                    for i in range(0, len(boxes), 4):
                        name_to_data[im_name].append(boxes[i : i + 4])

            progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

            for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
                img_names_batch = []
                for image_path in img_pathes_batch:
                    im_name = get_file_name_with_ext(image_path)
                    if "Negative" in image_path:
                        im_name = "Negative_" + im_name
                    elif "Positive" in image_path:
                        im_name = "Positive_" + im_name
                    img_names_batch.append(sub_ds + "_" + im_name)

                img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]

                anns = [create_ann(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns)

                progress.iters_done_report(len(img_names_batch))

    return project
