# occmodeler

`occmodeler` is described in:

> [Rob Walton and David De Roure. 2019. Modelling web based socio-technical systems through formalising possible sequences of human experience. In Proceedings of 11th ACM Conference on Web Science, Boston, MA, USA, June 30-July 3, 2019 (WebSci ’19), 10 pages.](https://doi.org/10.1145/3292522.3326049)

Interactive versions of the paper's figures are [here](https://robwalton.github.io/posts/2019/websci19/), but here is a static image showing two communities fighting out differing opinions on a single issue.

<img src="docs/images/websci19-figure-13-static.png" width="400">

See `occ's` [Jupyter notebook tutorial](occ/tutorial.ipynb) and the [experiment notebook](models/websci19/notebook.ipynb) for the paper.

## Dependencies and Installation

You probably want to create python  [virtual environment](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) to install the code and its dependencies into.


1. Start with an empty directory:
    ```bash
    mkdir occmodeler_test_install
    cd occmodeler_test_install
    ```
2. Create a ```venv``` virtual environment and activate it:
    ```bash
    python3 -m venv occmodeller_venv      # Creates occmodeller_venv in your current directory
    source occmodeler_venv/bin/activate  # Activates the environment
    ```
   
3. Clone the ```occmodeler``` repo and ```cd``` into it:
    ```bash
    git clone https://github.com/robwalton/occmodeler.git
    cd occmodeler
    ```
    
4. Install python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    Note that the ```requirements.txt``` includes requirements from the three packages that form the occmodeler suite: ```pyspike```, ```occ``` and ```occdash```. ```occdash``` brings in ```dash``` and ```redis```. This takes a vew minutes on my machine.
    
 5. Install the three packages (```pyspike```, ```occ``` and ```occdash```) in the repo to the virtual environment.
    ```bash
    pip install -e ./pyspike
    pip install -e ./occ
    pip install -e ./occdash
    ```
    Note that the ```-e``` installs the package in developer mode. This means that the installed package links back to the repo you checked out. Leave the ```-e``` if you have no inclination to edit the source code!
    
 6. Install [Spike](https://www-dssz.informatik.tu-cottbus.de/DSSZ/Software/Spike). Spike is downloaded as a directory including an executable with a version in its name. ```occmodeler``` currently expects to find Spike at ```~/bin/spike```. 
    
    So, download the Spike folder and out it somewhere. Create the ```~/bin``` if necessary and link the spike executable. For example:
    ```bash
    mkdir -p ~/bin
    ln -s <DIR_TO_KEEP_SOFTWARE>/spike-1.4.4-osx64/spike-1.4.4-osx64 ~/bin/spike
    ```
    Check the install with:
    ```bash
    ~/bin/spike version
    ```

## Tutorial

Try out the tutorial notebook.

Make sure your virtual environment is activated with:

```bash
source occmodeler_venv/bin/activate
```

Start jupyter-lab or jupyter-notebook (you will need to install these in your virtual environment unless you made this from a python install which included them).

```bash
pip install jupyter
```

Open ```<downloaded_occmodeller_repo>/occ/tutorial.ipynb```

## Models from WebSci'19 paper.

Open ```<downloaded_occmodeller_repo>/models/websci19/notebook.ipynb```



## Dependency issues

`occmodeller` depends on the closed source [Spike](https://www-dssz.informatik.tu-cottbus.de/DSSZ/Software/Spike) software. This is a risk as Spike ships with no license and so cannot be included here. Old versions of Spike are not available for download. I am in communication with Spike's developers whom seem keen to help with the problem however!

## Development

### Structure

The occmodeller repo currently contains three packages

1. `pyspike` will contain only code which is Spike specific. The package is undergoing a refactor in which other code is being distributed between...

2. `occ` contains the interface to occmodeller and everything which is not specifically Spike dependent although this may be difficult without considerable time spent on it.

3. `occdash` is a Plotly dashboard current for viewing the results of simulations captured with Sacred.




