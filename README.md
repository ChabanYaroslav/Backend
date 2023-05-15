# Backend
TODOs:

		Yaroslav 
		- records of permitted license plates (db related)
		- log capturing (db related)
		- command and control for RPI (MQTT)
			- takes pictures from RPI
			- sends back proper state of the gate (open gate or close gate; toggle)
			- sends back proper gate of the light (turn on or off; toggle)
			- receive states of the actuators
		Lukas
		- read license plates from the images and change state of the bar if necessary
		- Rest API
			- Get/Edit/Remove license plates
			- Get images
			- Get log records
			- Set light state
			- Set bar state
