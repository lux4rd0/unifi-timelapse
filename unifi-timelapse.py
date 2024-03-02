import os
import aiohttp
import asyncio
import datetime
import logging
import config
import aiofiles
import signal


# Configuring logging
logging.basicConfig(
    level=config.UNIFI_TIMELAPSE_LOGGING_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class CameraImageFetcher:
    def __init__(self, session):
        self.cameras = config.UNIFI_TIMELAPSE_CAMERAS
        self.image_output_path = config.UNIFI_TIMELAPSE_IMAGE_OUTPUT_PATH
        self.fetch_interval = config.UNIFI_TIMELAPSE_FETCH_INTERVAL
        self.url_pattern = config.UNIFI_TIMELAPSE_URL_PATTERN
        self.max_retries = config.UNIFI_TIMELAPSE_FETCH_MAX_RETRIES
        self.retry_delay = config.UNIFI_TIMELAPSE_FETCH_RETRY_DELAY
        self.session = session

    async def create_directory_structure(self, camera_name):
        """Create directory structure for storing images."""
        today = datetime.datetime.now()
        year, month, day = (
            today.strftime("%Y"),
            today.strftime("%m"),
            today.strftime("%d"),
        )
        path = os.path.join(self.image_output_path, camera_name, year, month, day)
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Created directory: {path}")
        return path

    async def fetch_and_save_image(self, session, camera_name, image_path):
        """Fetch image from the camera and save it to the specified path asynchronously with retries."""
        url = self.url_pattern.format(camera_name=camera_name)
        timeout = aiohttp.ClientTimeout(total=config.UNIFI_TIMELAPSE_FETCH_HTTP_TIMEOUT)

        for attempt in range(self.max_retries):
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.read()
                        if len(content) == 0:
                            logging.warning(
                                f"Received empty image for {camera_name}. Skipping save."
                            )
                            return

                        filename = f"{camera_name}_{int(datetime.datetime.now().timestamp())}.jpg"
                        filepath = os.path.join(image_path, filename)
                        async with aiofiles.open(filepath, "wb") as f:
                            await f.write(content)
                        logging.info(f"Image saved: {filepath}")
                    else:
                        logging.warning(
                            f"Failed to fetch image for {camera_name}, Status code: {response.status}"
                        )
                    return  # Exit the function after handling the response

            except asyncio.CancelledError:
                logging.info(f"Fetch task for {camera_name} was cancelled.")
                return  # Exit the function cleanly
            except aiohttp.ClientError as e:
                logging.error(
                    f"HTTP client error for {camera_name} on attempt {attempt + 1}/{self.max_retries}: {e}"
                )
            except asyncio.TimeoutError:
                logging.error(
                    f"Timeout error for {camera_name} on attempt {attempt + 1}/{self.max_retries}"
                )
            except Exception as e:
                logging.error(
                    f"General error for {camera_name} on attempt {attempt + 1}/{self.max_retries}: {e}"
                )

            try:
                await asyncio.sleep(self.retry_delay)
            except asyncio.CancelledError:
                # Handle cancellation during the sleep period
                logging.info(
                    f"Sleep interrupted for {camera_name} due to cancellation."
                )
                break  # Break the loop to stop further retries

    async def run(self):
        """Main method to run the image fetcher."""
        async with aiohttp.ClientSession() as session:
            while True:
                start_time = datetime.datetime.now()
                tasks = []
                for camera in self.cameras:
                    image_path = await self.create_directory_structure(camera)
                    task = asyncio.create_task(
                        self.fetch_and_save_image(session, camera, image_path)
                    )
                    tasks.append(task)

                # Gather tasks and handle exceptions
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle results and exceptions
                for result in results:
                    if isinstance(result, Exception):
                        logging.error(f"Task resulted in an error: {result}")

                elapsed_time = datetime.datetime.now() - start_time
                sleep_time = max(0, self.fetch_interval - elapsed_time.total_seconds())
                next_fetch_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=sleep_time
                )
                logging.info(
                    f"Next fetch in {sleep_time:.2f} seconds at {next_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                try:
                    await asyncio.sleep(sleep_time)
                except asyncio.CancelledError:
                    logging.info("Sleep interrupted due to shutdown.")
                    break  # Exit the while loop to end the run method

    async def cleanup(self):
        # Example: Close the session if it's not already closed
        if not self.session.closed:
            await self.session.close()
            logging.info("HTTP session closed.")

        # Add other cleanup tasks here
        logging.info("Cleanup tasks completed.")


async def main():
    logging.info("Starting Unifi Timelapse Fetcher")

    # Create an instance of the fetcher
    session = aiohttp.ClientSession()
    fetcher = CameraImageFetcher(session)

    # Setup graceful shutdown
    loop = asyncio.get_running_loop()

    for signame in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda signame=signame: asyncio.create_task(
                shutdown(getattr(signal, signame), fetcher, session)
            ),
        )

    try:
        await fetcher.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await fetcher.cleanup()


async def shutdown(signum, fetcher, session):
    signame = signal.Signals(signum).name
    logging.info(f"Received exit signal {signame}...")

    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    # Await the cancellation of all tasks
    await asyncio.gather(*tasks, return_exceptions=True)

    await fetcher.cleanup()
    await session.close()
    logging.info("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
