import argparse
import os
import time
import threading

from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler

import cli

import netifaces
import pychromecast


htdocs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "htdocs")
os.chdir(htdocs)
server = HTTPServer(("0.0.0.0", 45114), SimpleHTTPRequestHandler)
thread = threading.Thread(target=server.serve_forever)
thread.daemon = True


def server_up():
    thread.start()
    print("starting server on port {}".format(server.server_port))


def server_down():
    server.shutdown()
    print("stopping server on port {}".format(server.server_port))


def audio_play(chromecastip, filename):
    """Start playing music"""

    url = "http://{}:{}/{}".format(
        netifaces.ifaddresses("eth0")[netifaces.AF_INET][0]["addr"], 45114, filename
    )

    cast = pychromecast.Chromecast(chromecastip)
    cast.connect()
    cast.wait()
    mc = cast.media_controller
    mc.play_media(url, "audio/mp3")
    time.sleep(5)


def check_qos_enabled(interface):
    result = cli.execute("show policy-map interface {} output".format(interface))
    if len(result) == 0:
        return False
    else:
        return True


def config_qos(interface, policymap, desired):
    if desired is False:
        prefix = "no "
    else:
        prefix = ""

    cli.configure(
        [
            "interface {}".format(interface),
            "{}service-policy output {}".format(prefix, policymap),
            "end",
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chromecastip", help="IP Address of Chromecast", required=True
    )
    parser.add_argument(
        "--interface", help="Interface name to enable QoS", required=True
    )
    parser.add_argument(
        "--policymap",
        help="Name of the policy map that is applied to the interface",
        required=True,
    )
    args = parser.parse_args()

    status = check_qos_enabled(args.interface)

    server_up()

    if status is True:
        config_qos(args.interface, args.policymap, False)
        audio_play(args.chromecastip, "OFF.mp3")
    elif status is False:
        config_qos(args.interface, args.policymap, True)
        audio_play(args.chromecastip, "ON.mp3")

    server_down()


if __name__ == "__main__":
    main()
