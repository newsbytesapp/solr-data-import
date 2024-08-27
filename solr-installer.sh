#!/bin/bash

function install_solr() {
    local solr_version=$1

    sudo apt update && sudo apt install -y default-jdk
    java -version

    wget https://dlcdn.apache.org/solr/solr/$solr_version/solr-$solr_version.tgz
    tar xzf solr-$solr_version.tgz solr-$solr_version/bin/install_solr_service.sh --strip-components=2
    sudo bash ./install_solr_service.sh solr-$solr_version.tgz
}

function create_core() {
    local core_name=$1

    sudo su - solr -c "/opt/solr/bin/solr create -c $core_name -n data_driven_schema_configs"
    echo "Core $core_name created. Please edit your schema at /var/solr/data/$core_name/conf/managed-schema.xml"
    echo "Please edit your conf here: /etc/default/solr.in.sh"
    echo "To create more cores, use this:"
    echo "sudo su - solr -c \"/opt/solr/bin/solr create -c CORE_NAME -n data_driven_schema_configs\""
}

function initialize_and_add_crontab() {
    local core_name=$1

    cp env.example .env.$core_name

    echo "Adding crontab entries for automated index update..."

    (crontab -l 2>/dev/null; echo "* * * * * python3 $(pwd)/importer.py -c $core_name >> $(pwd)/solr-delta-log.$core_name.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 2 */2 * * python3 $(pwd)/importer.py -c $core_name -r >> $(pwd)/solr-delta-log.$core_name.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 0 * * * rm $(pwd)/solr-delta-log.$core_name.log 2>&1") | crontab -

    echo "Crontab entries added:"
    echo "* * * * * python3 $(pwd)/importer.py -c $core_name >> $(pwd)/solr-delta-log.$core_name.log 2>&1"
    echo "0 2 */2 * * python3 $(pwd)/importer.py -c $core_name -r >> $(pwd)/solr-delta-log.$core_name.log 2>&1"
    echo "0 0 * * * rm $(pwd)/solr-delta-log.$core_name.log 2>&1"
}

function display_help() {
    echo "Usage: $0 [option] [argument]"
    echo "Options:"
    echo "  --install-solr VERSION        Install Solr with the specified version"
    echo "  --create-core CORE_NAME       Create a Solr core with the specified name"
    echo "  --initialize CORE_NAME        Initialize and add crontab for the specified core name"
    echo "  --help                        Display this help message"
    echo ""
    echo "Examples:"
    echo "  Install Solr:"
    echo "    $0 --install-solr 8.11.1"
    echo ""
    echo "  Create a Solr core:"
    echo "    $0 --create-core my_core"
    echo ""
    echo "  Initialize and add crontab entries for a core:"
    echo "    $0 --initialize my_core"
}

case $1 in
    --install-solr)
        install_solr $2
        ;;
    --create-core)
        create_core $2
        ;;
    --initialize)
        initialize_and_add_crontab $2
        ;;
    --help)
        display_help
        ;;
    *)
        echo "Invalid option. Use --help to see the valid options."
        ;;
esac
