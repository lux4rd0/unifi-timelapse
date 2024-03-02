import os

# CAMERA CONFIGURATIONS
# List of camera names to fetch images from
UNIFI_TIMELAPSE_CAMERAS = os.getenv(
    "UNIFI_TIMELAPSE_CAMERAS",
    "cam-basement,cam-basement-tenlog,cam-frontdoor,cam-garage,cam-lavalamp,cam-pergolanorth,cam-pergolasouth",
).split(",")

# DOMAIN AND URL CONFIGURATIONS
# Domain for fetching images
UNIFI_TIMELAPSE_DOMAIN = os.getenv("UNIFI_TIMELAPSE_DOMAIN", "tylephony.com")
# URL pattern for fetching images
UNIFI_TIMELAPSE_URL_PATTERN = (
    f"http://{{camera_name}}.{UNIFI_TIMELAPSE_DOMAIN}/snap.jpeg"
)

# PATH CONFIGURATIONS
# Base path for storing images
UNIFI_TIMELAPSE_IMAGE_OUTPUT_PATH = os.getenv(
    "UNIFI_TIMELAPSE_IMAGE_OUTPUT_PATH", "output/images"
)
# Base path for video output
UNIFI_TIMELAPSE_VIDEO_OUTPUT_PATH = os.getenv(
    "UNIFI_TIMELAPSE_VIDEO_OUTPUT_PATH", "output/video"
)

# FETCH AND RETRY CONFIGURATIONS
# Interval between fetches in seconds
UNIFI_TIMELAPSE_FETCH_INTERVAL = int(os.getenv("UNIFI_TIMELAPSE_FETCH_INTERVAL", 60))
# Maximum number of retries for each fetch attempt
UNIFI_TIMELAPSE_FETCH_MAX_RETRIES = int(
    os.getenv("UNIFI_TIMELAPSE_FETCH_MAX_RETRIES", 3)
)
# Delay between retries in seconds
UNIFI_TIMELAPSE_FETCH_RETRY_DELAY = int(
    os.getenv("UNIFI_TIMELAPSE_FETCH_RETRY_DELAY", 5)
)
# Timeout for HTTP requests in seconds
UNIFI_TIMELAPSE_FETCH_HTTP_TIMEOUT = int(os.getenv("UNIFI_TIMELAPSE_HTTP_TIMEOUT", 10))

# LOGGING CONFIGURATION
# Logging level (e.g., 'INFO', 'ERROR', 'DEBUG')
UNIFI_TIMELAPSE_LOGGING_LEVEL = os.getenv(
    "UNIFI_TIMELAPSE_LOGGING_LEVEL", "INFO"
).upper()
