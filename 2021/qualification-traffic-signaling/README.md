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
Initial solutions are created and saved and panda dataframe (CSV format) in directory "intermediate"
The first argument is the input filename and the second (number) is the number of solutions required.
```sh
python3 generate.py a_example.txt 100 &
python3 generate.py b_by_the_ocean.txt 100 &
python3 generate.py c_checkmate.txt 100 &
python3 generate.py d_daily_commute.txt 100 &
python3 generate.py e_etoile.txt 100 &
python3 generate.py f_forever_jammed.txt 100 &

```

### 2. Optimize initial solutions
Using genetic algorithms below commands will optimize the initial solutions and save the new solutions also in the "intermediate" directory
```sh
python3 optimize.py a_example &
python3 optimize.py b_by_the_ocean &
python3 optimize.py c_checkmate &
python3 optimize.py d_daily_commute &
python3 optimize.py e_etoile &
python3 optimize.py f_forever_jammed &


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

