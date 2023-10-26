import matplotlib.pyplot as plt
import time
from pyscope.observatory import SimulatorServer, ASCOMCamera
# run this by
# sudo python3 vb.py

s = SimulatorServer()
# increase more time if error kept happening
time.sleep(10)

c = ASCOMCamera('localhost:32323', alpaca=True)
c.Connected = True
c.StartExposure(60, True)
while not c.ImageReady:
    print('not ready')
    time.sleep(5)
im = c.ImageArray
plt.imshow(im)
plt.show()
c.Connected = False
del s
