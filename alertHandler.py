import sys
import logging
import datetime
import os
import yaml
from ratelimit import limits
import requests

script_dir = os.path.split(os.path.realpath(__file__))[0]  # get where the script is

logging.basicConfig(filename=script_dir+'/alertHandler.log',level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Starting alertHandler")
count = 0

def write_stdout(s):
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()

def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()

def data_to_dict(data):
    try:
        data = data.split()  # split up string by spaces and turn it into a list
        return dict(
            s.split(':') for s in data)  # go through the list of strings and convert them to a dictionary item
    except Exception as e:
        logging.warning(f"An error occurred while converting data to a dictionary: {e}")

def notify_user(headers, data, recvTime):
    try:
        crashInfo = data_to_dict(data)  # convert data to a easy dictionary
        crashInfo["to_state"] = headers.get("eventname").replace("PROCESS_STATE_", "") # get the new process state out of headers, rename and put it somewhere more useful.
        pName = crashInfo.get("processname")
        if pName in config:
            pData = config.get(pName)
            if crashInfo.get("to_state") in pData.get("alerts"):
                logging.info("Found process "+pName)
                sendMsg(recvTime, crashInfo, config.get(pName), logging)
            else:
                logging.info(f"{crashInfo.get('to_state')} is not used")
        else:
            logging.info("Could not find process "+pName)

    except Exception as e:
        logging.warning("Exception notify_user:" + str(e))

def main():
    while 1:
        # transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')

        # read header line and print it to stderr
        line = sys.stdin.readline()
        write_stderr(line)

        # read event payload and print it to stderr
        headers = dict([ x.split(':') for x in line.split() ])
        data = sys.stdin.read(int(headers['len']))
        write_stderr(data)

        notify_user(headers, data, str(datetime.datetime.now()))

        # transition from READY to ACKNOWLEDGED
        write_stdout('RESULT 2\nOK')


# maybe split this part out into a seperate file if it gets too big again?
def formatMessage(recvTime, crashInfo, message, logging):
    fmtstr = ["{{process_name}}", "{{timestamp}}", "{{from_state}}", "{{to_state}}"]
    fmtout = [crashInfo.get("processname"), recvTime, crashInfo.get("from_state"), crashInfo.get("to_state")]
    for x in range(0, len(fmtstr)):
        logging.info(f"Replacing {fmtstr[x]} with {fmtout[x]}")
        message = message.replace(fmtstr[x], fmtout[x])
    logging.info(f"Formatted message to: {message}")
    return message

@limits(calls=100, period=1200)
def sendMsg(recvTime, crashInfo, pData, logging):
    try:
        message = formatMessage(recvTime, crashInfo, pData.get("message_format"), logging)
        r = requests.post(url=pData.get("webhookURL"), json={'content': message})
        logging.info(r.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception {e}")
    except Exception as e:
        logging.error(e, exc_info=True)

if __name__ == '__main__':
    f = open(script_dir+"/config.yaml", "r+")
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.info(config)
    main()
    f.close()