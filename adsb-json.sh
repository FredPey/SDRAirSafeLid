#:/env/ bash

./dump1090/dump1090 --forward-mlat --dcfilter --write-json-every 1 --write-json /home/pi/fichier_json --mlat --gain 100 --interactive --net-bind-address [rpi_ip_address] --net-ro-port 15555 --metric --net
