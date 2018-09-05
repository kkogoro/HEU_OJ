wget https://github.com/quark-zju/lrun/releases/download/v1.1.4/lrun_1.1.4_amd64.deb
sudo apt-get install -y libseccomp2 build-essential clisp fpc gawk gccgo gcj-jdk ghc git golang lua5.2 mono-mcs ocaml openjdk-8-jdk perl php-cli python2.7 python3 racket rake ruby valac rlwrap
sudo dpkg -i lrun_1.1.4_amd64.deb
sudo gpasswd -a $USER lrun
wget https://deb.nodesource.com/node/pool/main/n/nodejs/nodejs_0.10.46-1nodesource1~xenial1_amd64.deb
sudo dpkg -i nodejs_0.10.46-1nodesource1~xenial1_amd64.deb
git clone https://github.com/8cbx/ljudge.git
cd ljudge
make 
sudo make install
sudo cp -r ./etc/ljudge /etc/ljudge