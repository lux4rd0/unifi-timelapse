import os
import shutil
import datetime
import subprocess
import argparse
import config


def create_timelapse(days_ago, camera_name):
    date = datetime.datetime.now() - datetime.timedelta(days=days_ago)

    date_year = date.strftime("%Y")
    date_month = date.strftime("%m")
    date_day = date.strftime("%d")

    image_path = f"{config.UNIFI_TIMELAPSE_IMAGE_OUTPUT_PATH}/{camera_name}/{date_year}/{date_month}/{date_day}"
    video_path = f"{config.UNIFI_TIMELAPSE_VIDEO_OUTPUT_PATH}/{date_year}/{date_month}/{camera_name}"

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    docker_command = [
        "docker",
        "run",
        "-v",
        f"{os.getcwd()}:{os.getcwd()}",
        "-v",
        "/mnt/attic:/mnt/attic",
        "-w",
        os.getcwd(),
        "jrottenberg/ffmpeg:4.4-alpine",
        "-stats",
        "-r",
        "30",
        "-f",
        "image2",
        "-pattern_type",
        "glob",
        "-i",
        f"{image_path}/{camera_name}_*.jpg",
        "-c:v",
        "libx265",
        "-preset",
        "medium",
        "-crf",
        "25",
        "-pix_fmt",
        "yuv420p",
        "-tag:v",
        "hvc1",
        f"{video_path}/{camera_name}_{date_year}{date_month}{date_day}.mp4",
    ]

    subprocess.run(docker_command)

    shutil.rmtree(image_path)


def main():
    parser = argparse.ArgumentParser(
        description="Create a timelapse video from camera images."
    )
    parser.add_argument(
        "days_ago", type=int, help="Number of days ago to create timelapse for"
    )
    parser.add_argument("camera_name", type=str, help="Name of the camera")

    args = parser.parse_args()
    create_timelapse(args.days_ago, args.camera_name)


if __name__ == "__main__":
    main()
