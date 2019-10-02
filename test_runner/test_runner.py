import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import notify2
import subprocess as sub

from datetime import datetime

FolderNameToWatchForFileChanges = "/var/www/html/foldername/"
dir_path = os.path.dirname(os.path.realpath(__file__))

import random

GLOBAL_NOTIFICATION_INSTANCE = notify2.init('foo')
n = notify2.Notification("", "", "")


def notifiyUser(title, description, IsPassed):

    if  IsPassed:
        n.update(title, description, os.path.join(dir_path, "success.png"))
    else:
        n.update(title, description, os.path.join(dir_path, "failure.png"))
    n.set_timeout(300)
    n.set_urgency(2)
    n.show()

def subprocess_cmd(command):
    process = sub.Popen(command,stdout=sub.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def runTests(filename):
    command = ["codecept",
                "run", "unit"
    ]
    for cmd in command:
        print(cmd, end=" ")

    result = subprocess_cmd('cd' + FolderNameToWatchForFileChanges + '; codecept run unit --debug')


    print("o/p is " + str(result))

    if "There was" in str(result) or "Errors" in str(result) or "failed" in str(result):
        IsPassed = False
    else:
        IsPassed = True


    if IsPassed:
        notifiyUser("passed", "all tests passed " + datetime.now().strftime('%H:%M:%S'), True)
    else:
        notifiyUser("failed", "test failure " + datetime.now().strftime('%H:%M:%S'), False)

def _check_modification(text):
    filename = os.path.basename(text)
    if filename.endswith(".php"):
        runTests(text)

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        _check_modification(event.src_path)

    def on_modified(self, event):
        _check_modification(event.src_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, FolderNameToWatchForFileChanges, recursive=True)
    observer.start()
    print("phpunit test watcher started -- GROWL --- ")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
