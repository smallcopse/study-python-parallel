import logging
import logging.handlers
import sys
def create_basic_logger(
    name, filepath, level=logging.DEBUG, stderr_level=None, file_level=None):

    # create logger
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    # create console handler and set level to debug
    seh = logging.StreamHandler(sys.stderr)
    if stderr_level:
        seh.setLevel(stderr_level)

    rfh = logging.handlers.RotatingFileHandler(filepath)
    if file_level:
        rfh.setLevel(file_level)

    # create formatter
    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')

    # add formatter
    seh.setFormatter(formatter)
    rfh.setFormatter(formatter)

    # add handlers to logger
    _logger.addHandler(seh)
    _logger.addHandler(rfh)

    return _logger