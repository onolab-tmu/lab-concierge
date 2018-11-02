# At some point implement useful commands

FIRMWARE_IMAGE=firmware/esp32-20180405-v1.9.3-520-gb9c78425.bin
PORT?=${AMPY_PORT}

.PHONY: uslackclient
uslackclient:
	git clone git@github.com:fakufaku/uslackclient.git 2> /dev/null || echo "uslackclient already exists"
	make -C uslackclient deploy

.PHONY: uwebsockets
uwebsockets:
	git clone git@github.com:fakufaku/uwebsockets.git 2> /dev/null || echo "uwebsockets already exists"
	make -C uwebsockets deploy

.PHONY: logging
logging:
	git clone https://github.com/micropython/micropython-lib.git 2> /dev/null || echo "micropython-lib already exists"
	ampy put micropython-lib/logging/logging.py logging.py

barista: logging uwebsockets uslackclient
	make -C barista deploy

.PHONY: barista-clean
barista-clean:
	ampy rm logging.py
	make -C uwebsockets clean
	make -C uslackclient clean
	make -C barista clean

# Clean up the local files used to keep track of modifications
.PHONY: reset
reset:
	rm -rf uwebsockets/__deploy__
	rm -rf uslackclient/__deploy__
	rm -rf barista/__deploy__

.PHONY: firmware
firmware:
	esptool.py --chip esp32 --port ${PORT} write_flash -z 0x1000 ${FIRMWARE_IMAGE}

.PHONY: erase_flash
erase_flash:
	esptool.py --chip esp32 --port ${PORT} erase_flash
