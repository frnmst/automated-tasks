Running
=======

Prepare environment
-------------------

The ``./prepare_environment.py`` script outputs a shell script based on the content
of the ``./metadata.yaml`` file.  All scripts are disabled by default. Have a look
at the ``enabled`` fields in the metadata file. Once you are done editing you can
run the script like this


::


    $ ./prepare_environment.py prepare_environment.conf > prepare_environment.sh


Now, check the ``./prepare_environment.sh`` before running it as `root`


::


    # chmod +x ./prepare_environment.sh && ./prepare_environment.sh


This script also copies ``./deploy.py``.

Deploy
------

The ``./deploy.py`` script copies the systemd unit files from the services by-user
directory to the appropriate systemd directory. It also start and enables the
newly copied systemd timer files. If a timer file is not available, the service
file is enabled and started instead.

If needed, edit the hard-coded ``SRC_DIR`` variable in the script.

