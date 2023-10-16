from pyscope.observatory import SimulatorServer, ASCOMTelescope
sim = SimulatorServer()

telescope = ASCOMTelescope('localhost:32323', alpaca=True)
telescope.Connected = True
telescope.SlewToAltAzAsync(45, 45)

del sim  # kill server so it doesn't run in the background and it resets every time
