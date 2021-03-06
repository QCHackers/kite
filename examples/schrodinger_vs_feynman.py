import kite as kt

prog = kt.Program(
    kt.QREG(2, probability_of_amplitude='00'),
    kt.H(0),
    kt.CNOT(0,1))

amplitude_from_schrodinger = kt.schrodinger(prog)
print("Amplitude from Schrodinger")
print(amplitude_from_schrodinger )


amplitude_from_feynman = kt.feynman(prog)
print("Amplitude from Feynman")
print(amplitude_from_feynman)

assert amplitude_from_schrodinger == amplitude_from_feynman