import os
import time
import logging
from threading import Event
from contextlib import closing
from slacker import Slacker
from periphery import GPIO
from gsmmodem.modem import GsmModem

logger = logging.getLogger(__name__)

PORT = "/dev/ttyAMA0"
BAUDRATE = 115200
POST_INIT_DELAY = 15
PIN = os.environ.get("PIN", None)

SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#smack")
slack = Slacker(os.environ["SLACK_API_TOKEN"])


def main():
    init_modem()
    time.sleep(POST_INIT_DELAY)

    modem = GsmModem(
        PORT,
        BAUDRATE,
        smsReceivedCallbackFunc=handle_sms,
        incomingCallCallbackFunc=handle_call,
    )
    
    modem.connect(PIN)
    
    # prevent `SMS FULL` URC, just process them
    # now if we still have old unprocessed SMS
    modem.processStoredSms()

    logger.info(" ✓ Waiting for calls / sms...")
    Event().wait()


def init_modem():
    with closing(GPIO(4, "out")) as gpio4:
        gpio4.write(False)
    with closing(GPIO(6, "out")) as gpio6:
        gpio6.write(False)


def handle_sms(sms):
    slack.chat.post_message(
        channel=SLACK_CHANNEL,
        attachments=[{
            "color": "#55e3c7",
            "title": "SMS from {}".format(sms.number),
            "footer": sms.time.strftime("%m/%d/%Y, %H:%M:%S") if sms.time else None,
            "text": sms.text,
        }],
    )


def handle_call(call):
    if call.ringCount >= 1:
        call.answer()
        call.hangup()

        slack.chat.post_message(
            channel=SLACK_CHANNEL,
            attachments=[{
                "color": "#e37155",
                "title": "Call from {}".format(call.number if call.number else "Unknown"),
                "text": "The incoming call has been answered.",
            }],
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
