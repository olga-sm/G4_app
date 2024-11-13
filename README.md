# G4_app
With this repository it is possible to connect to the Polhemus G4 using a dongle. 

## 1. initialize_system(cfr_file)
Used to initialize the system. The configuration file needs to be given as a parameter. Without this step, it is impossible to connect to the system. *Serial* is not possible, because of the RF-linking. The dongle-id **must** be used for all other function.
