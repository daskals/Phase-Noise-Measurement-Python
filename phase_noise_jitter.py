#######################################################
#     Spyros Daskalakis                               #
#     last Revision: 19/12/2023                       #
#     Python Version:  3.9                            #
#     Email: Daskalakispiros@gmail.com                #
#######################################################

import sys
import pyvisa

# Setup the Signal Analyzer
VISA_ADDRESS = 'USB0::0x2A8D::0x1C0B::MY60112463::INSTR'  # Replace with your instrument's VISA address

try:
    # Establish a connection (session) with the instrument
    resourceManager = pyvisa.ResourceManager()
    mymxa = resourceManager.open_resource(VISA_ADDRESS)
    mymxa.timeout = 30000  # Timeout set to 30000 milliseconds (30 seconds)
except pyvisa.Error as ex:
    print(f"Couldn't connect to '{VISA_ADDRESS}'. Error: {ex}. Exiting now...")
    sys.exit()

# Configuration for Phase Noise Measurement
center_frequency = 15e6  # Center frequency set to 15 MHz (adjust as needed)

# Switch the instrument to Phase Noise mode
mymxa.write("INST:SEL PNOISE")
# Configure the display to show phase noise on a logarithmic scale
mymxa.write("CONFigure:LPLot:NDEFault")

# Reset the instrument to clear status registers and error queue
mymxa.write("*CLS")

# Set the center frequency for phase noise measurements
mymxa.write(f"FREQ:CENT {center_frequency}")

# ------------- Marker 1: Phase Noise Measurement -------------
# Place Marker 1 at a specified frequency offset for phase noise measurement
marker1_offset = 10e3  # Offset set to 10 kHz
mymxa.write(f"CALC:LPLot:MARK1:X {marker1_offset}")

# ------------- Marker 2: Jitter Measurement -------------
# Place Marker 2 at a different specified frequency offset for jitter measurement
marker2_offset = 5e3  # Offset set to 5 kHz
mymxa.write(f"CALC:LPLot:MARK2:X {marker2_offset}")
mymxa.write("CALC:LPLot:MARK2:FUNC RMSN")
mymxa.write("CALC:LPLot:MARK2:RMSN:MODE JITTer")

# Set the bandwidth spans for jitter measurement
left_band_span_min = 1e3  # Left band span set to minimum (1 kHz)
right_band_span_max = 9e3  # Right band span set to 9 kHz
mymxa.write(f"CALC:LPLot:MARK2:BAND:LEFT {left_band_span_min}")
mymxa.write(f"CALC:LPLot:MARK2:BAND:RIGH {right_band_span_max}")

# Initiate the measurement and wait for completion
mymxa.write("INIT:IMM;*OPC?")
try:
    mymxa.read()
except pyvisa.errors.VisaIOError as e:
    print(f"Timeout occurred: {e}. Consider increasing the timeout or checking instrument settings.")

# Retrieve phase noise measurement at Marker 1
phase_noise_dbc = mymxa.query_ascii_values("CALC:LPLot:MARK1:Y?")

# Retrieve integrated jitter measurement at Marker 2
jitter_in_seconds = mymxa.query_ascii_values("CALC:LPLot:MARK2:Y?")

# Convert jitter measurement from seconds to picoseconds
jitter_in_picoseconds = jitter_in_seconds[0] * 1e12  # Conversion factor: 1 second = 1e12 picoseconds

# Display the measured phase noise and jitter
print(f"Measured Phase Noise at {marker1_offset/1e3} kHz offset: {phase_noise_dbc[0]} dBc/Hz")
print(f"Measured Jitter at {marker2_offset/1e3} kHz offset: {jitter_in_picoseconds} picoseconds")

# Close the connection to the instrument
mymxa.close()