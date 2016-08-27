# timeseriesdash


Dependencias
============

sudo apt-get install libyaml-dev libpython2.7-dev
sudo apt-get install postgresql-server-9.3-dev libffi-dev

virtualenv .
source bin/activate
pip install -r deps.txt

sudo apt-get install nodejs-legacy
sudo apt-get install npm
sudo npm install -g bower
bower install bower.json 

python generate.py metrics-commodities.yaml 2010-01-01 2016-07-31 

