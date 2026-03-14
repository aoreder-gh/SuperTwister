echo "try to install all updates for python3"
sudo apt install mc python3-pigpio python3-pil python3-dev python3-smbus i2c-tools inkscape python3-pil.imagetk -y
pip3 install --break-system-packages adafruit-blinka
pip install  --break-system-packages adafruit-circuitpython-ads1x15
echo "installation done"