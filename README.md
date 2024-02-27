<h1 align="center">🚢 Port Simulation 🚛 </h1>

<h3 align="center">
    <p>"A platform used for researching the coordination of autonomous vehicles to optimize the efficiency of transport and other collaborative tasks."</p>
</h3>
<p align="center">
    <a href="https://github.com/OpenBMB/AgentVerse/blob/main/LICENSE">
        <img alt="License: Apache2" src="https://img.shields.io/badge/License-Apache_2.0-green.svg">
    </a>
    <a href="https://www.python.org/downloads/release/python-3916/">
        <img alt="Documentation" src="https://img.shields.io/badge/python-3.7+-blue.svg">
    </a>
</p>

<p align="center">
<img src="./docs/port_traffic.png" width="425">
</p>

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
export SUMO_HOME="/opt/homebrew/opt/sumo/share/sumo"
```
Notice that you will not be able to run with sumo-gui or with multiple simulations in parallel if this is active ([more details](https://sumo.dlr.de/docs/Libsumo.html)).





### Experiments

Check experiments for examples on how to instantiate an environment.

```bash
python3 experiments/simulator.py -config config/port.ini
```
<p align="center">
<img src="./docs/port1.png" width="425">
</p>
| **[SUMO]**          |                               |             |
| ------------------- | ----------------------------- | ----------- |
| nets                | 路网定义文件路径              | ： .net.xml |
| route               | 路由定义文件路径              | ： .rou.xml |
| num_seconds         | 仿真时间步step                | ：int       |
|                     |                               |             |
| delta_time          | Env执行action的step间隔时间步 | default = 1 |
| edges_start_default | 车辆默认初始位置（边）        |             |
| begin_time          | sumo仿真起始时间步            | default = 0 |
|                     |                               |             |
|                     |                               |             |
| **[RENDER]**        |                               |             |
| gui                 | 是否可视化sumo                | ：bool      |



## MDP - Observations, Actions and Rewards

### Observation

<!-- start observation -->

The default observation for each traffic signal agent is a vector:
```python
obs = []
```
You can define your own observation by implementing a class that inherits from ObservationFunction and passing it to the environment constructor.

![image-20231221202534826](C:\Users\wyf\AppData\Roaming\Typora\typora-user-images\image-20231221202534826.png)

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





