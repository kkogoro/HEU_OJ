sudo rm -rf /usr/local/bin/ljudge
sudo rm -rf /etc/ljudge
make clean
make
sudo make install
sudo cp -r ./etc/ljudge /etc/ljudge