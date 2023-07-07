import csv
import glob
import os
from collections import defaultdict
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import (
    dir_exists,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s


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
    dataset_path = "/home/iwatkot/supervisely/ninja-datasets/road-potholes"
    batch_size = 30

    images_path = "/home/iwatkot/supervisely/ninja-datasets/road-potholes/Dataset 1 (Simplex)/Dataset 1 (Simplex)"
    annotations_file = "train_df.csv"
    img_height = 2760
    img_wight = 3680

    def create_ann(image_path):
        labels = []

        file_name = get_file_name(image_path)

        image_data = name_to_data.get(file_name)
        if image_data is not None:
            for curr_image_data in image_data:
                bboxes = list(map(int, curr_image_data))

                left = bboxes[0]
                top = bboxes[1]
                right = bboxes[0] + bboxes[2]
                bottom = bboxes[1] + bboxes[3]
                rect = sly.Rectangle(left=left, top=top, right=right, bottom=bottom)
                label = sly.Label(rect, obj_class)
                labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    obj_class = sly.ObjClass("pothole", sly.Rectangle)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[obj_class])
    api.project.update_meta(project.id, meta.to_json())

    anns_path = os.path.join(dataset_path, annotations_file)

    name_to_data = defaultdict(list)
    with open(anns_path, "r") as file:
        csvreader = csv.reader(file)
        for idx, row in enumerate(csvreader):
            if idx != 0:
                name_to_data[row[0]].append(row[2:])

    for ds_folder in os.listdir(images_path):
        curr_ds_path = os.path.join(images_path, ds_folder)
        if dir_exists(curr_ds_path):
            ds_name = ds_folder.split(" ")[0]

            dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

            if ds_name == "Train":
                images_pathes = glob.glob(images_path + "/*/*/*.JPG")
            else:
                images_pathes = glob.glob(images_path + "/*/*.JPG")

            progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

            for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
                img_names_batch = []
                for image_path in img_pathes_batch:
                    im_name = get_file_name_with_ext(image_path)
                    if "Negative" in image_path:
                        im_name = "Negative_" + im_name
                    img_names_batch.append(im_name)

                img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]

                anns = [create_ann(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns)

                progress.iters_done_report(len(img_names_batch))

    return project
