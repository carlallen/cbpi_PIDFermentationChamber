# PID Setpoint Fermentation Chamber Logic for CraftBeerPi

Use this Controller Logic to automatically control the setpoint for a fermentation chamber

## Installation

Download and Install this Plugin via the CraftBeerPi user interface
or pull into the [craftbeerpi]/modules/plugins/ directory

## Fermenter Configuration

* Sensor1: Beer Temperature
* Sensor2: Chamber Temperature
* Sensor3: Not Used
* Compressor Delay: The time in minutes to wait between compressor cycles
* Kp: The is the proportional gain for the PID (Default 2)
* Ki: The the integral gain for the PID (Default 0.0001)
* Kd: The the derivative gain for the PID (Default 2)
