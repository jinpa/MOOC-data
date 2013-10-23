# RunExternal.py
# author = Jonathan Huang
# usage: RunExternal(["./someProg", "arg1"], 5).go() to run someProg, but 
#       kill it if it takes more than 5 seconds

import subprocess as sub
import threading

class RunExternal(threading.Thread):
    def __init__(self, cmd, timeout,pipeOption = False):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout
        self.pipeOption = pipeOption

    def run(self):
        if self.pipeOption:
            self.runWithPipe()
        else:
            self.runWithoutPipe()

    def runWithoutPipe(self):
        self.killed = False
        self.p = sub.Popen(self.cmd)
        self.p.wait()
        self.outputcode = self.p.returncode

    def runWithPipe(self):
        self.killed = False
        self.p = sub.Popen(self.cmd, bufsize = -1, stdout = sub.PIPE)
        self.p.wait()
        self.outputcode = self.p.returncode
        self.outLines = self.p.stdout.readlines()

    def go(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.kill()
            self.killed = True
            self.join()


