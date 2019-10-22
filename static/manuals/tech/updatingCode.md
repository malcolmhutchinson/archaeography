Updating the server's codebase
==============================


We deploy to `/opt/archaeography/code`.  The codebase there is a clone
of the github repository, with an added branch `deploy`. This branch
holds changes in the settings files that are different in the deployed
environment to those in a development environment (the `master` branch).

In order to update the deployed codebase, perform these steps.

1.  Make changes, merge to the `master` branch and push to github.

1.  On the server, checkout the `master` branch, and pull from github.

1.  Checkout the `deploy` branch and merge the changes from `master`.

1.  Restart the apache server.