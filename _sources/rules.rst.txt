Rules
=====

Basics
------

- all the scripts, this documentation and their dependencies are `free software <https://www.gnu.org/philosophy/free-sw.html>`_.

Structure
`````````

- scripts and systemd unit files are divided by categories and placed in different directories
  accordingly. See the ``./src`` directory
- if files are imported into a script, these will be classified as
  configuration files
- scripts cannot run without configuration files
- scripts or systemd unit files are optional:

  - standalone systemd unit file does the job in some cases. In this case configuration files are not needed
  - a script does not need a systemd unit file if it is called directly by an external program

Dependencies
~~~~~~~~~~~~

Scripts page 
............

- dependencies are referred to the machine where the services need to be installed
- the versions reported here are valid at the moment of writing

References page
...............

- the list of software is as generic as possible

File naming
-----------

Configuration and systemd unit files follow naming schemes that make easier to relate multiple services to configurations and multiple
configurations to scripts.

Variables
`````````

================            =======================              ======================
Variable                    Configuration file name              Systemd unit file name
================            =======================              ======================
``script_name``             ``_`` separated words                ``-`` separated words
``subject``                 ``_`` separated words                ``_`` separated words
================            =======================              ======================

Rules
`````

- optional variables and constants are reported between square brackets (``[`` and ``]``)

============================    ====================================================    =================================================
Script                          Configuration                                           Systemd unit file
============================    ====================================================    =================================================
``${script_name}.{py,sh}``      ``${script_name}.[${subject}.]{conf,options}``          ``${script_name}.[${subject}.]{service,timer}``
============================    ====================================================    =================================================

Scripts page schemas
--------------------

Generic rules
`````````````

- optional elements must be omitted if empty

Variables
~~~~~~~~~

====================         =============================================================================================
Variable name                Description
====================         =============================================================================================
``${script_name}``           the name of the script
``${category_name}``         the name of the category that identifies the directory where the source file have been placed
``${running_user}``          see the ``List of runing users`` section in the references page
``${path_i}``                the path of a file
``${yaml_data}``             see the ``YAML data sections`` schema
====================         =============================================================================================

The YAML data sections schema
`````````````````````````````

The following schema represents a single entry for the ``YAML data`` section.

.. code-block:: yaml
    :linenos:

    <--YAML-->                                  # required
    ${script_name}:                             # required
        category: ${category_name}              # required
        running user: ${running_user}           # required
        configuration files:
            paths:
                - ${path_i}                     # 0->n
        systemd unit files:
            paths:
                service:
                    - ${path_i}                 # 0->n
                timer:
                    - ${path_i}                 # 0->n
    <!--YAML-->
    

.. important:: Since `commit 8852e61 <https://github.com/frnmst/automated-tasks/commit/8852e6109bbf6bfffcadaf2727e62f6f4eed3e67>`_ 
               the metadata file is generated dynamically using the 
               ``YAML data`` sections of the scripts documentation.

Schema
``````

The following schema represents a single entry.


.. code-block:: html
    :linenos:


    <h3>${script_name}</h3>             # required
    <h4>Purpose</h4>                    # required
    <p></p>                             # required
    <h4>Steps</h4>                      # an implicit step for all the scripts is to edit the configuration file{,s}
    <ol>                                
        <li></li>                       # 1->n
    </ol>
    <h4>References</h4>
    <ul>
        <li></li>                       # 1->n
    </ul>
    <h4>Programming languages</h4>      # required
    <ul>                                # required
        <li></li>                       # required, 1->n
    </ul>
    <h4>Dependencies</h4>               # required
    <table>
        <tr>                            # required
            <th>Name</th>
            <th>Binaries</th>
            <th>Version</th>
        </tr>
        <tr>                            # required
            <td></td>                   # requited
            <td>
                <ul>
                    <li></li>           # 0->n
                </ul>
            </td>
            <td></td>                   # required
        </tr>
    </table>
    </table>
    <h4>Configuration files</h4>
    <p></p>
    <h4>Systemd unit files</h4>
    <p></p>
    <h4>Licenses</h4>                   # required
    <ul>                                # required
        <li></li>                       # required, 1->n
    </ul>
    <h4>YAML data</h4>                   # required
    <pre>                               # required
        ${yaml_data}                    # required, see the YAML data sections schema
    </pre>
    <hr />                              # required
