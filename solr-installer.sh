#!/bin/solr

sudo apt update && sudo apt install default-jdk
java -version

wget https://dlcdn.apache.org/solr/solr/$1/solr-$1.tgz
tar xzf solr-$1.tgz solr-$1/bin/install_solr_service.sh --strip-components=2
sudo bash ./install_solr_service.sh solr-$1.tgz

sudo su - solr -c "/opt/solr/bin/solr create -c $2 -n data_driven_schema_configs"

echo "Please edit your schema at /var/solr/data/$2/conf/managed-schema.xml"

echo "To create more cores, please use this:"
echo "sudo su - solr -c \"/opt/solr/bin/solr create -c $2 -n data_driven_schema_configs\""

cp .env.example .env.$2

echo "Please put this crontab entry for automated index update:"
echo "* * * * * python $(pwd)/importer.py $2 >> /dev/null 2>&1"
