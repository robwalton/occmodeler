# occmodeller

`occmodeler` is described in:

> Rob Walton and David De Roure. 2019. Modelling web based socio-technical systems through formalising possible sequences of human experience. In Proceedings of 11th ACM Conference on Web Science, Boston, MA, USA, June 30-July 3, 2019 (WebSci ’19), 10 pages.

Interactive versions of the papers figures are [here](https://robwalton.github.io/posts/2019/websci19/), but here is a static image showing two communities fighting out differing opinions on a single issue.

<img src="docs/images/websci19-figure-13-static.png" width="400">

A PDF of the paper will be available soon.

See `occ's` [Jupyter notebook tutorial](occ/tutorial.ipynb) and the [experiment notebook](models/websci19/notebook.ipynb) for the paper.

## Dependencies and Installation

For now, check out the whole repo. It includes PyCharm configuration for paths.

## Dependencies

`occmodeller` depends on the closed source [Spike](https://www-dssz.informatik.tu-cottbus.de/DSSZ/Software/Spike) software. This is a risk as Spike ships with no license and so cannot be included here. The version of `occmodeler` here has been written against Spike 1.0.1 which is currently unavailable for download. I am in communication with Spike's developers!

## Development

### Structure

The occmodeller repo currently contains three packages

1. `pyspike` will contain only code which is Spike specific. The package is undergoing a refactor in which other code is being distributed between...

2. `occ` contains the interface to occmodeller and everything which is not specifically Spike dependent although this may be difficult without considerable time spent on it.

3. `occdash` is a Plotly dashboard current for viewing the results of simulations captured with Sacred.

These depend on each other from bottom to top. As the code settles I will make these pypi package and fixup dependencies and testing. For now the software includes a PyCharm project which sets up these dependencies.


