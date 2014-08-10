"""
Cam tests.
"""

import time, image, logging

def runtests(opt, stream):
    """
    Run *count* of tests, - images will be saved to the temp folder.
    Side comparison.
    """
    for _ in range(0, opt.test):
        image1 = image.frombytes(stream.getimagebytes())
        if opt.mask:
            image.mask(image1, opt.mask)
        time.sleep(opt.pause)
        image2 = image.frombytes(stream.getimagebytes())
        if opt.mask:
            image.mask(image2, opt.mask)
        difference = image.diff(image1, image2)
        if difference >= opt.motionat:
            image.save(
                image.combine(
                    image1,
                    image2,
                    "%s // %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), difference)
                ),
                opt.storage
            )
            logging.info("!! Motion detected: %s" % difference)
        else:
            logging.debug("No motion detected: %s" % difference)
