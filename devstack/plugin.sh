#!/bin/bash

# forecasting plugin for DevStack

function install_forecasting {
    echo_summary "Installing AI Forecasting Plugin"

    # Install Python dependencies
    pip_install -r $PROGETTO_DIR/requirements.txt

    # Install the package in development mode
    setup_develop $PROGETTO_DIR
}

function configure_forecasting {
    echo_summary "Configuring AI Forecasting Plugin"

    # Create directories
    sudo install -d -o $STACK_USER /var/log/forecasting
    sudo install -d -o $STACK_USER /etc/forecasting

    # Create configuration file
    cat > /etc/forecasting/forecasting.conf << EOF
[DEFAULT]
debug = True
log_dir = /var/log/forecasting

[api]
host = 0.0.0.0
port = 5005
EOF
}

function init_forecasting {
    echo_summary "Initializing AI Forecasting Service"

    # Start the service
    run_process forecasting-api "python $PROGETTO_DIR/forecasting_plugin/api.py"
}

function stop_forecasting {
    echo_summary "Stopping AI Forecasting Service"
    stop_process forecasting-api
}

# check for service enabled
if is_service_enabled forecasting; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services for Forecasting"

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Forecasting"
        install_forecasting

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Forecasting"
        configure_forecasting

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the forecasting service
        echo_summary "Initializing Forecasting"
        init_forecasting
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down forecasting services
        echo_summary "Stopping Forecasting"
        stop_forecasting
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        echo_summary "Cleaning up Forecasting"
        # Remove log files
        sudo rm -rf /var/log/forecasting
    fi
fi