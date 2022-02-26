# Setting up system service files
for s in read_data; do
	sudo cp ~/airthings-waveplus-beacon/services/${s}.service /lib/systemd/system/${s}.service
 	sudo systemctl enable ${s}
done
