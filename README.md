# SDRAirSafeLid

SDRAirSafeLid is the main software of an original and low-cost ADS-B based system to fulfill air traffic safety obligations during atmospheric high power lidar operation.

If you use SDRAirSafeLid please cite the following reference:

"Peyrin F., Fréville P., Montoux N., Baray J.-L., Original and low-cost ADS-B system to fulfill air traffic safety obligations during atmospheric high power lidar operation. [paper to be submitted to reviews before publication] submitted to Sensors journal, Jan. 2023"


# Summary
Lidar is an atmospheric sounding technique based on the use of high-power lasers.
The use of these lasers involves fulfilling obligations with respect to air safety. 
As the lidar is equipped with a class 4 laser potentially dangerous for aircraft flying overhead the lidar, the air traffic surveillance including the possibility to shut off the laser is required by the international regulations.

Here, we present a low-cost air traffic surveillance solution integrated into an automated operating system for the Rayleigh-Mie-Raman lidar of the OPGC, Clermont Ferrand.
Our original system is based on Software Defined Radio (SDR).
The ADS-B transponder frames are acquired and analyzed in real-time, and the laser emission is stopped during lidar operation when an aircraft is detected within a 2 km radius around the lidar.
During the initial period of validation, Laser shutdowns due to the detection of aircraft near the Clermont Ferrand lidar caused a data loss rate of less than 2%.
The system has been accredited in 2019 by the French air traffic authorities.

# Installation
This package needs:
* Dump1090: https://github.com/MalcolmRobb/dump1090
* Python 2.7, and the additional packages json, os, datetime, time, socket

# Author
* Frédéric Peyrin (f.peyrin@opgc.fr)
* OPGC, UAR833, CNRS, Université Clermont Auvergne

# License
* GNU General Public License v3.0
* Source code must be made available when the software is distributed.
* See the LICENSE file for details
* https://www.gnu.org/licenses/gpl-3.0.txt
