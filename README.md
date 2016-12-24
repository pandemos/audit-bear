# Audit Bear
Audit Bear is a web application to analyze audit log data from the iVotronic
electronic voting machines and detect various anomalies and problems.

Exported from code.google.com/p/audit-bear

## Setup

This requires web2py from http://www.web2py.com/init/default/download
It does not have a requirements.txt file, so good luck. Not using a virtualenv, I needed to install:
- matplotlib

Once you have the dependencies, symlink this repository's `web2py/applications/audit_bear` into web2py's `applications/` directory. At least, that appears to work.

To run the application: `python /path/to/web2py/web2py.py -a <admin_password> .`
Note that there are a lot of command-line switches that can take. `python web2py.py -h` will tell you about them.

By default it binds to localhost on port 8000.
