import logging
import sys

# Create a logger
logger = logging.getLogger("projectz")
logger.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(module)s] - %(message)s"
)

# Create a file handler
file_handler = logging.FileHandler("projectz.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
