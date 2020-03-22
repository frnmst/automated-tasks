Running
=======

Go into the ``./utils`` directory and execute these steps:

1. generate the ``metadata.yaml`` file
2. generate a shell script, called  ``prepare_environment.sh``, based on the content of the ``metadata.yaml`` file.
3. run the ``prepare_environment.sh`` script as root.


.. code-block:: bash
    :linenos:


    ./prepare_environment.py prepare_environment.conf --generate-yaml > metadata.yaml       # step 1
    ./prepare_environment.py prepare_environment.conf > prepare_environment.sh              # step 2
    chmod +x ./prepare_environment.sh
    ./prepare_environment.sh                                                                # step 3


Services and timers
-------------------

Once everyting is installed you can run the usual systemd commands such as:


.. code-block:: bash
    :linenos:


    systemctl list-timers
    systemctl status ${service_or_timer} 
    systemctl start ${service_or_timer} 
    systemctl stop ${service_or_timer} 
    systemctl enable ${service_or_timer} 
    systemctl disable ${service_or_timer} 
    systemctl daemon-reload


with ``${service_or_timer}`` being the service or timer unit file names reported
between the YAML sections in the scripts page.
