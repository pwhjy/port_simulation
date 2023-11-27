<!-- start install -->

### Install SUMO latest version:

```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc
```
Don't forget to set SUMO_HOME variable (default sumo installation path is /usr/share/sumo)
```bash
echo 'export SUMO_HOME="/usr/share/sumo"' >> ~/.bashrc
source ~/.bashrc
```
Important: for a huge performance boost (~8x) with Libsumo, you can declare the variable:
```bash
export LIBSUMO_AS_TRACI=1
```
Notice that you will not be able to run with sumo-gui or with multiple simulations in parallel if this is active ([more details](https://sumo.dlr.de/docs/Libsumo.html)).



## MDP - Observations, Actions and Rewards

### Observation

<!-- start observation -->

The default observation for each traffic signal agent is a vector:
```python
    obs = []
```
You can define your own observation by implementing a class that inherits from ObservationFunction and passing it to the environment constructor.

<!-- end observation -->

### Action

<!-- start action -->

The action space is discrete.

<!-- end action -->

### Rewards

<!-- start reward -->

It is also possible to implement your own reward function:

```python
env = SumoEnvironment(..., reward_fn=my_reward_fn)
```

<!-- end reward -->

### Experiments

Check experiments for examples on how to instantiate an environment.

```bash
python experiments/simulator.py
```
