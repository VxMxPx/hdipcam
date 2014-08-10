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
        self._strikes = self._def_strikes = opt.strikes
        self._stream = stream
        self._motionat = opt.motionat
        self._temp = opt.temp
        self._mask = opt.mask
        self._storage = opt.storage
        # opt.fps = 4
        self._timestop = round(1000 / (opt.fps * 1000), 4)
        self._fps = opt.fps

    def captureframe(self, position, timelimit=None):
        """
        Save single image, as *position* to temp folder.
        """
        logging.debug("Frame: %s", position)
        try:
            frame = image.frombytes(self._stream.getimagebytes())
        except Exception as exc:
            self._bad_requests += 1
            logging.warning("Failed to get image: %s", str(exc))
            return
        self._bad_requests = 0
        diff = 0.0
        if not timelimit and (position % self._fps == 0 or position == 1):
            framem = copy.copy(frame)
            if self._keyframe:
                if self._mask:
                    image.mask(framem, self._mask)
                diff = image.diff(framem, self._keyframe)
                logging.debug("Difference while recording: %s", diff)
                if diff >= self._motionat:
                    self._strikes = self._def_strikes
                else:
                    self._strikes = self._strikes -1
            self._keyframe = framem
        saveframe(frame, self._temp, position,
                  params=(time.strftime("%Y-%m-%d %H:%M:%S"), round(diff, 4), position))

    def record(self, startat=1, timelimit=None):
        """
        Start the recording process.
        Clear temp folder, produce movie.
        """
        threads = []
        k = startat
        self._keyframe = None
        self._bad_requests = 0
        self._strikes = self._def_strikes
        while True:
            proc = threading.Thread(
                target=self.captureframe, args=(k, timelimit))
            threads.append(proc)
            proc.start()
            logging.debug("Strikes: %s", self._strikes)
            # if k > startat + self._fps and not self._keyframe:
            #     logging.warning("Round %d and still no image. "
            #                     "Waiting 15 seconds to recover.", k)
            #     time.sleep(15)
            if self._bad_requests > 20:
                logging.warning("More than 20 bad request in a row. Terminated.")
                break
            if self._strikes == 0:
                logging.info("Out of strikes. Recoding stopped.")
                break
            if timelimit and k * self._timestop > timelimit:
                logging.info("Time limited recoding. Done.")
                break
            time.sleep(self._timestop)
            k += 1

        [proc.join() for proc in threads]
        # time.sleep(5)
        producemovie(self._temp, self._fps, self._storage)
        emptytemp(self._temp)

    def watchdog(self):
        """
        Watch for motion, when detected start recording
        """
        buffer = []
        bframe = None
        while True:
            # keep buffer 4 frames long
            if len(buffer) > 4:
                buffer = buffer[-4:]
            # try to get image from device
            try:
                frame = image.frombytes(self._stream.getimagebytes())
            except Exception:
                buffer = []
                bframe = None
                logging.warning("Watchdog request timeout. Sleep for 2s.")
                time.sleep(2)
                continue
            buffer.append(copy.copy(frame))
            if self._mask:
                image.mask(frame, self._mask)
            if not bframe:
                bframe = frame
                time.sleep(1)
                continue
            difference = image.diff(bframe, frame)
            if difference >= self._motionat:
                logging.info("!! Motion detected: %s", difference)
                bufflen = len(buffer)
                threading.Thread(target=saveframes, args=(buffer,self._temp)).start()
                bframe = None
                self.record(bufflen + 1)
            else:
                logging.debug("No motion detected: %s", difference)
                bframe = frame
                time.sleep(1)


def saveframes(frames, dest):
    """
    Save images to the destination.
    """
    for k, frame in enumerate(frames):
        saveframe(frame, dest, k + 1,
                  params=(time.strftime("%Y-%m-%d %H:%M:%S"), "BUFFER", k + 1))

def saveframe(frame, dest, filename,
              caption="DATE: %s | DIFF: %s | FRAME: %s", params=()):
    """
    Save image with watermark.
    """
    filename = str(filename)
    filename = filename.rjust(12, "0")
    image.watermark(frame, caption % params)
    image.save(frame, dest, filename)

def producemovie(temp, fps, storage):
    """
    Call system ffmpeg to merge images into movie.
    """
    logging.info("Starting to produce movie.")
    temp = temp + r"'*.jpg'"
    storage = storage + ("%s.mp4" % time.strftime("%Y-%m-%d-%H-%M-%S"))
    subprocess.call(
        # "ffmpeg -r %s -i %s -framerate 23 -c:v libx264
        # %s" % (fps, temp, storage),
        "ffmpeg -r %s -f image2 -pattern_type glob -i "
        "%s -c:v libx264 %s"
        % (fps, temp, storage),
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
