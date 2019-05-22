# Plans

# Some ideas to forget


## Architecture
* https://community.plot.ly/t/live-update-by-pushing-from-server-rather-than-polling-or-hitting-reload/23468 for pushing to an open dash view.
* Use https://github.com/plotly/jupyterlab-dash to open a dash dashboard for each run OR move to ipywidgets.
* https://github.com/nteract/papermill may help with below, or replace the primitive libraries for example with just interactive code. https://medium.com/netflix-techblog/scheduling-notebooks-348e6c14cfd6

* Create a SystemModel variant which includes the python code to create the model and or initial conditions and (perhaps in a form that takes depedency injection like e.g. pytest or Spring) . Include this in the model run. IT should take the form of Jupyter notebook which results in a SystemModel object which can be run. Each time the notebook file is passed to SimRunner the git repo it is in is commited. If we allow that the resulting output files form a subrepo and we commit only after these have run then we would also get the evoloution of the files. Each run...

* Build the GUI out of Jupyter Lab. Create a url or [command](https://jupyterlab.readthedocs.io/en/stable/user/urls.html#managing-workspaces-cli) to open a workspace from every past run. Clicking on this generates a clone as the original run can't be changed. This clone will have the files used to create the model copied from the run to a temprary staging area where they can be changed and either run, left open as a workspace in a queue of experiments to run, or acting as the basis of ones planned to run much later. If run they will be archived permenantly in the system we have now. This results in a lot of duplication. Having the model being something we keep in git and each time perhaps we push it to server this triggers a run resulting in a set of files attached to the original push by a subsequent commit or just by commit-id. In this system a repo holds a branch for each new model we want to develop.

* Clone workspace for the last run (or any other past run) to create the basis for the next. Keep a directed graph of runs in this way.
