Rules
=====

Basics
------

- everything in this repository is `free software <https://www.gnu.org/philosophy/free-sw.html>`_.

Structure
`````````

- scripts and systemd unit files are placed in different directories
  according to categories.
- if files are imported into a script, these will be classified as
  configuration files
- scripts cannot run without configuration files
- scripts or systemd unit files are optional:

  - a standalone systemd unit file does the job in some cases. In this case configuration files are not needed
  - a script does not necessarly need a systemd unit file

Dependencies
~~~~~~~~~~~~

- the reported software versions are valid at the moment of writing

File naming
-----------

Configuration and systemd unit files follow naming schemes that make easier to relate multiple services to configurations and multiple
configurations to scripts.

Variables
`````````

================            ======================================              =====================================
Variable                    Configuration file name word separator              Systemd unit file name word separator
================            ======================================              =====================================
*script_name*               ``_``                                               ``-``
*subject*                   ``_``                                               ``_``
================            ======================================              =====================================

- optional variables and constants are reported between square brackets (``[`` and ``]``)

============================    ====================================================    =================================================
Script                          Configuration                                           Systemd unit file
============================    ====================================================    =================================================
``${script_name}.{py,sh}``      ``${script_name}.[${subject}.]{conf,options}``          ``${script_name}.[${subject}.]{service,timer}``
============================    ====================================================    =================================================

Scripts page
------------

Variables
`````````

====================         =============================================================================================
Variable name                Description
====================         =============================================================================================
``${script_name}``           the name of the script
``${category_name}``         the name of the category that identifies the directory where the source file have been placed
``${running_user}``          see the ``List of runing users`` section in the references page
``${path_i}``                the path of a file
====================         =============================================================================================

Schema
``````

.. important:: Since `commit 8852e61 <https://github.com/frnmst/automated-tasks/commit/8852e6109bbf6bfffcadaf2727e62f6f4eed3e67>`_ 
               the metadata file is generated dynamically using the 
               ``YAML data`` sections of the scripts documentation.

.. important:: Optional elements must be omitted if empty.


The following schema represents a single entry translated into HTML.


.. code-block:: html
    :linenos:


    <h3>${script_name}</h3>                             # required
    <img src="assets/image/${script_name}_${i}">        # i = 0->n
    <h4>Purpose</h4>                                    # required
    <p></p>                                             # required
    <h4>Examples</h4>                    
    <p></p>
    <h4>Steps</h4>                                      # an implicit step for all the scripts is to edit the configuration file{,s}
    <ol>                                
        <li></li>                                       # 1->n
    </ol>
    <h4>References</h4>
    <ul>
        <li></li>                                       # 1->n
    </ul>
    <h4>Programming languages</h4>                      # required
    <ul>                                                # required
        <li></li>                                       # required, 1->n
    </ul>
    <h4>Dependencies</h4>                               # required
    <table>
        <tr>                                            # required
            <th>Name</th>
            <th>Binaries</th>
            <th>Version</th>
        </tr>
        <tr>                                            # required
            <td></td>                                   # requited
            <td>
                <ul>
                    <li></li>                           # 0->n
                </ul>
            </td>
            <td></td>                                   # required
        </tr>
    </table>
    </table>
    <h4>Configuration files</h4>
    <p></p>
    <h4>Systemd unit files</h4>
    <p></p>
    <h4>Licenses</h4>                                   # required
    <ul>                                                # required
        <li></li>                                       # required, 1->n
    </ul>
    <h4>YAML data</h4>                                  # required
    <pre>                                               # required
        <--YAML-->                                      # required
        ${script_name}:                                 # required
            category: ${category_name}                  # required
            running user: ${running_user}               # required
            configuration files:
                paths:
                    - ${path_i}                         # i = 0->n
            systemd unit files:
                paths:
                    service:
                        - ${path_i}                     # i = 0->n
                    timer:
                        - ${path_i}                     # i = 0->n
        <!--YAML-->
    </pre>
    <hr />                                              # required
