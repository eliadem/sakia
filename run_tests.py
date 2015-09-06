import sys
import os
import signal
import unittest
import subprocess
import time
import shlex

cmd = 'python -m pretenders.server.server --host 127.0.0.1 --port 50000'

p = subprocess.Popen(shlex.split(cmd))
time.sleep(2)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

print("Run")
runner = unittest.TextTestRunner().run(unittest.defaultTestLoader.discover(start_dir='cutecoin.tests', pattern='test_*'))
print("Terminate")
os.kill(p.pid, signal.SIGINT)
time.sleep(2)

try:
    os.kill(p.pid, signal.SIGKILL)
    p.kill()
    print("Hard killed")
except OSError:
    print("Terminated gracefully")

sys.exit(not runner.wasSuccessful())