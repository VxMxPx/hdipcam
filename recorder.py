"""
Contains recorder class.
"""

import time, image, threading, os, subprocess, copy, logging

class Recorder(object):
    """
    Capture series of images to temp folder and merge them to video.
    """
    def __init__(self, opt, stream):
        self._keyframe = None
        self._bad_requests = 0
        self._strikes = opt.strikes
        self._stream = stream
        self._opt = opt

    def putimage(self, position):
        """
        Save singlee image, as *position* to temp folder.
        """
        logging.debug("Frame: %s", position)

        try:
            frame = image.frombytes(self._stream.getimagebytes())
        except Exception:
            self._bad_requests += 1
            logging.warning("Request timeout.")
            return

        diff = 0.0

        if self._bad_requests > 0:
            self._bad_requests -= 1
        if position % 4 == 0 or position == 1:
            if self._keyframe:
                diff = image.diff(frame, self._keyframe)
                logging.debug("Difference while recording: %s", diff)
                if diff >= self._opt.motionat:
                    self._strikes = self._opt.strikes
                else:
                    self._strikes = self._strikes -1
            self._keyframe = copy.copy(frame)
        image.watermark(
            frame,
            "DATE: %s | DIFF: %f | FRAME: %s"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), diff, position))
        image.save(frame, self._opt.temp, position)

    def record_motion(self, startat=8):
        """
        Start recording and stop when there's no more motion.
        """
        threads = []
        k = startat
        self._keyframe = None
        self._bad_requests = 0
        self._strikes = self._opt.strikes
        while True:
            proc = threading.Thread(target=self.putimage, args=(k,))
            proc.start()
            threads.append(proc)
            logging.debug("Strikes: %s", self._strikes)
            if k > startat + 4 and not self._keyframe:
                logging.warning("Round %d and still no image. "
                                "Waiting 15 seconds to recover.", k)
                time.sleep(15)
            if self._bad_requests > 10:
                logging.warning("More than 20 bad request. Terminated.")
                break
            if self._strikes == 0:
                logging.info("Out of strikes. Recoding stopped.")
                break
            time.sleep(0.25)
            k += 1
        return threads

    def record(self, startat=8):
        """
        Start the recording process.
        Clear temp folder, produce movie.
        """
        threads = self.record_motion(startat)
        for proc in threads:
            proc.join()
        producemovie(self._opt.temp, self._opt.storage)
        emptytemp(self._opt.temp)

    def putbuffer(self, buffer):
        """
        Save images from buffer.
        """
        for k, frame in enumerate(buffer):
            image.watermark(
                frame,
                "DATE: %s | BUFFER" % time.strftime("%Y-%m-%d %H:%M:%S"))
            image.save(frame, self._opt.temp, k + 1)
        buffer = []

    def watchdog(self):
        """
        Watch for motion, when detected start recording
        """
        buffer = []
        while True:
            if len(buffer) > 4:
                buffer = buffer[-4:]
            try:
                image1 = image.frombytes(self._stream.getimagebytes())
                time.sleep(self._opt.pause)
                image2 = image.frombytes(self._stream.getimagebytes())
            except Exception:
                logging.warning("Watchdog request timeout. Sleep for 2s.")
                time.sleep(2)
                continue
            if self._opt.mask: image.mask(image1, self._opt.mask)
            if self._opt.mask: image.mask(image2, self._opt.mask)
            buffer.append(image1)
            buffer.append(image2)
            difference = image.diff(image1, image2)
            if difference >= self._opt.motionat:
                logging.info("!! Motion detected: %s", difference)
                threading.Thread(target=self.putbuffer, args=(buffer,)).start()
                self.record(len(buffer) + 1)
            else:
                logging.debug("No motion detected: %s", difference)


def producemovie(temp, storage):
    """
    Call system ffmpeg to merge images into movie.
    """
    logging.info("Starting to produce movie.")
    temp = temp + r"%d.jpg"
    storage = storage + ("%s.mp4" % time.strftime("%Y-%m-%d-%H-%M-%S"))
    subprocess.call(
        "ffmpeg -r 4 -i %s -framerate 23 -c:v libx264 %s" % (temp, storage),
        shell=True)

def emptytemp(temp):
    """
    Remove files from temp folder.
    """
    logging.info("Emptying temp directory: %s", temp)
    for file in os.listdir(temp):
        file_path = os.path.join(temp, file)
        try:
            if os.path.isfile(file_path):
                logging.debug("Delete: %s", file)
                os.unlink(file_path)
        except Exception:
            logging.warning("Couldn't unlink the file %s", file_path)
