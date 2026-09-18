import os

# Disable the file handler so running the tests does not append to the user's
# facilito.log. Must happen before any test module imports facilito.logger.
os.environ["FACILITO_LOG_FILE"] = ""
