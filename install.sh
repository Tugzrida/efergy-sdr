#/bin/bash
printf "\e[92mInstalling efergy-sdr...\e[39m\n"
printf "\e[92mInstalling dependencies...\e[39m\n"
sudo apt-get -y update
sudo apt-get -y install libtool libusb-1.0.0-dev librtlsdr-dev rtl-sdr python-requests git cmake
printf "\e[92mCloning rtl_433...\e[39m\n"
git clone https://github.com/merbanan/rtl_433.git /tmp/rtl_433/
printf "\e[92mBuilding rtl_433...\e[39m\n"
mkdir /tmp/rtl_433/build/
cd /tmp/rtl_433/build/
cmake ../
make
sudo make install
cd /home/pi/
rm -r /tmp/rtl_433/
echo "# This system has librtlsdr0 installed in order to
# use digital video broadcast receivers as generic
# software defined radios.
blacklist dvb_usb_rtl28xxu
blacklist e4000
blacklist rtl2832" | sudo tee /etc/modprobe.d/rtl-sdr-blacklist.conf

printf "\e[92mCloning efergy-sdr...\e[39m\n"
git clone https://github.com/Tugzrida/efergy-sdr.git ~/efergy-sdr/
chmod +x ~/efergy-sdr/capture.py ~/efergy-sdr/post.py
printf "\e[92mDone! Now follow the setup info at https://github.com/Tugzrida/efergy-sdr#setup\e[39m\n"
