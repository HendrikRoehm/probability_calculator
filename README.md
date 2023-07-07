[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
![build-with-hatch](https://github.com/HendrikRoehm/probability_calculator/actions/workflows/python-package-with-hatch.yml/badge.svg)

# probability_calculator

Calculate with and analyze random variables / probability densities.

## Usage

Install the package, e.g.: `pip install probability_calculator`.

### Initialization and plotting

The package provides simple ways to define random variables with discrete outcomes, for instance a die:


```python
from probability_calculator import FairDie

density = FairDie(6) # initialize a fair die with 6 sides
fig, ax = density.plot_outcomes() # plot the outcomes using matplotlib
```


    
![png](README_files/README_1_0.png)
    


For the general case, the class `RandomVariables` can be used:


```python
from probability_calculator import RandomVariable
from fractions import Fraction

density = RandomVariable(outcomes=[
    { "value": 0, "p": Fraction(2, 10) },
    { "value": 1, "p": Fraction(3, 10) },
    { "value": Fraction(5, 2), "p": Fraction(1, 10) },
    { "value": 3, "p": Fraction(4, 10) },
]) # initialize a discrete density with 4 different outcomes
fig, ax = density.plot_outcomes() # plot the density using matplotlib
```


    
![png](README_files/README_3_0.png)
    


Note that only integers and fractions can be used to assure exact calculations.

### Combine random variables

The discrete density of throwing a die two times can be modelled by adding the random variable with itself:


```python
density_for_one_throw = FairDie(6)
density_sum_of_two_throws = density_for_one_throw + density_for_one_throw # same as density_for_one_throw*2
fig, ax = density_sum_of_two_throws.plot_outcomes()
```


    
![png](README_files/README_5_0.png)
    


Note that the operations (`+` and `*`) on random variables are always assuming independed random variables, even when using the same variable multiple times.

## Limitations

Continuous densities / random variables are not supported at the moment.

Adding many random variables together might get stuck due to a lot of possible outcomes. In general, adding 10 densities with 10 outcomes each lead to $10^{10}$ outcomes. However, simple cases like the die work, so even `Die(10)*100` is no problem.


## Contributing
We greatly appreciate fixes and new features for [probability_calculator](https://github.com/HendrikRoehm/probability_calculator). All contributions to this project should be sent as pull requests on github.

## License

[Apache License 2.0](LICENSE)
