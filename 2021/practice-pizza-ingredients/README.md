<h1 align="center">

Even more pizza

</h1>
<p>
<img alt="Version" src="https://img.shields.io/badge/version-0.0.1-blue.svg?cacheSeconds=2592000" />

<a href="https://twitter.com/Bikxs" target="_blank"><img alt="Twitter: Bikxs" src="https://img.shields.io/twitter/follow/Bikxs.svg?style=social" /></a>
</p>

> Hash Code practice problem


## Install
Create a conda enviroment and install the python libraries listed in requirements.txt
```sh
conda create -n env_more_pizza python=3.7
conda activate env_more_pizza
pip instal -r requirements.txt

```

## Usage
To get to the solution for the competition- a three stage pipeline is followed.
### 1. Generate initial solutions
Initial solutions are created and saved and panda dataframe (pickle format) in directory "intermediate"
The first argument is the input filename and the second (number) is the number of solutions required.
```sh
python3 generate.py a_example.in 100 &
python3 generate.py b_little_bit_of_everything.in 100 &
python3 generate.py c_many_ingredients.in 100 &
python3 generate.py d_many_pizzas.in 100 &
python3 generate.py e_many_teams.in 100 &

```

### 2. Optimize initial solutions
Using genetic algorithms below commands will optimize the initial solutions and save the new solutions also in the "intermediate" directory
```sh
python3 optimize.py a_example &
python3 optimize.py b_little_bit_of_everything &
python3 optimize.py c_many_ingredients &
python3 optimize.py d_many_pizzas &
python3 optimize.py e_many_teams &

```
### 3. Generate solutions for submission
Below command will scourge the "intermediate" directory, choose the best solution and save it in the requested format as per competions.
It will also create a zipped copy of the code for upload into the judge system. The solutions are saved in a folder called "output"
```sh
python3 compile_solutions.py
```

## Author
👤 **Stephen Biko Nyamai**

* Twitter: [@Bikxs](https://twitter.com/Bikxs)
* GitHub: [@Bikxs](https://github.com/Bikxs)
* LinkedIn: [@Bikxs](https://linkedin.com/in/Bikxs)

