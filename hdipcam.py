#!/usr/bin/env python

"""
Security Cam Recorder.
Support for: HDIPCAM MEYE-035366-CCFBB
"""

import logging, argparse, stream, test, recorder, time
from os.path import dirname, realpath, isdir

def initaruments():
    """
    Initialize command line arguments.
    """
    aparse = argparse.ArgumentParser(
        description="SecCam - a HD security camera recorder.")
    aparse.add_argument(
        "-i", "--ip",
        required=True,
        help="Camera's IP and port, for example: 192.168.1.1:8020")
    aparse.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information.")
    aparse.add_argument(
        "-s", "--strikes",
        default=8,
        type=int,
        help="How many seconds before termination of recording,"
        "if no motion detected.")
    aparse.add_argument(
        "-m", "--motionat",
        default=7,
        type=float,
        help="Level of difference to be considered motion.")
    aparse.add_argument(
        "-p", "--pause",
        default=1,
        type=int,
        help="Pause between two images (when comparing) in seconds.")
    aparse.add_argument(
        "-b", "--mask",
        help="Mask to be applied on image when comparing."
        "Format: top.left.width.height,top.left...")
    aparse.add_argument(
        "--temp",
        default="./temp",
        help="Temporary folder. WARNING: content will be removed."
        "(Start with dot for relative)")
    aparse.add_argument(
        "--storage",
        default="./storage",
        help="Video storage folder. (Start with dot for relative)")
    aparse.add_argument(
        "--log",
        help="Log file path. If empty logs will no be saved to a file. "
        "(Start with dot for relative)")
    aparse.add_argument(
        "--uri",
        default="/snapshot.cgi?user=%s&pwd=%s",
        help="Image URI, with username and password placeholders.")
    aparse.add_argument(
        "--user",
        default="",
        help="Login username, if required.")
    aparse.add_argument(
        "--password",
        default="",
        help="Login password, if required.")
    aparse.add_argument(
        "--test",
        type=int,
        help="Run in test mode, save N of images in comparison.")
    return aparse.parse_args()

def checkdirs(opt):
    """
    Verify that all selected directories are correct.
    """
    if opt.log:
        if opt.log[0:2] == "./":
            opt.log = dirname(realpath(__file__)) + opt.log[1:]
        if opt.log[-1] != "/":
            opt.log += "/"
        if not isdir(opt.log):
            raise ValueError("Invalid log path: `%s`. "
                             "Make sure that the folder exists or "
                             "use --log to change it. "
                             "Log path is optional." % opt.log)

    if opt.temp[0:2] == "./":
        opt.temp = dirname(realpath(__file__)) + opt.temp[1:]
    if opt.temp[-1] != "/":
        opt.temp += "/"
    if not isdir(opt.temp):
        raise ValueError("Invalid temp path: `%s`. "
                         "Make sure that the folder exists or "
                         "use --temp to change it." % opt.temp)
    if opt.storage[0:2] == "./":
        opt.storage = dirname(realpath(__file__)) + opt.storage[1:]
    if opt.storage[-1] != "/":
        opt.storage += "/"
    if not isdir(opt.storage):
        raise ValueError("Invalid storage path: `%s`. "
                         "Make sure that the folder exists or "
                         "use --storage to change it." % opt.storage)

def runapp(opt):
    """
    Process parameters, build objects and execute action(s).
    """
    if opt.mask:
        opt.mask = opt.mask.split(",")
        opt.mask = [tuple(mask.split(".")) for mask in opt.mask]
        opt.mask = tuple(opt.mask)
    streami = stream.Stream(opt.ip, opt.uri % (opt.user, opt.password))
    if opt.test:
        test.runtests(opt, streami)
    else:
        try:
            recorder.Recorder(opt, streami).watchdog()
        except KeyboardInterrupt:
            recorder.emptytemp(opt.temp)
            logging.info("Will empty the temp directory. Bye!")


def main():
    """
    Initialize the application from command line.
    """
    args = initaruments()
    try:
        checkdirs(args)
    except ValueError as e:
        print(str(e))
        return
    if args.log:
        args.log += time.strftime("%Y-%m-%d.log")
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        filename=args.log,
        format="%(levelname)s (%(asctime)s) %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("HDIPCAM Monitoring Started!")
    try:
        runapp(args)
    except KeyboardInterrupt:
        logging.info("Bye!")

if __name__ == "__main__":
    main()
