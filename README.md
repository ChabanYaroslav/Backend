# Backend
### Information regarding the API
In order to get access to the API, run `api_run`. This will make the API available on port 5000 where a demo implementation of a virtual device and database is attached.
If errors are encountered during development, please get in touch with @Lukas.

In order to plug in custom DB- and Device entities, the interfaces `IDevice` and `IDatabase` need to be implemented. Those are found in the server.py file located in the 'api' directory.
The methods implemented by the interface are commented to make the implementation easier.
The 'MemoryDevice' and 'MemoryDatabase' class are both working implementations of the interfaces and can be used for reference. 
Please, also make sure to update the container class and add the custom DB- and Device entity so that the API can access it.

### Information regarding the Plate Detection
Please install a conda environment. Find the conda.yml file in the conda directory. \
For an ugly demo implementation go to the `recognition_run` file. To access the plate recognition, first initiliaze a `Recognizer`object. Then run the method `detect()`with a valid `ImageEntity` object.
You should get the license plate number as a string.

## TODOs:

		Yaroslav 
		- records of permitted license plates (db related)
		- log capturing (db related)
		- command and control for RPI (MQTT)
			- takes pictures from RPI
			- sends back proper state of the gate (open gate or close gate; toggle)
			- sends back proper gate of the light (turn on or off; toggle)
			- receive states of the actuators
