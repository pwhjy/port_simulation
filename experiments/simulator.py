import argparse
import os
import time
import logging
import sys
import re

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sumo_rl.environment.port_env import *


if __name__ == "__main__":
    prs = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="""Q-Learning Single-Intersection""" )
    prs.add_argument("-config", dest="confpath", type=str, default="config/port.ini", required=False)
    args = prs.parse_args()

    # experiment_time = str(datetime.now()).split(".")[0]
    # experiment_time = re.sub(":", "_", experiment_time)

    env = SumoEnvironment(
        config_path = args.confpath,
    )

    initial_states = env.reset()
    done = {"__all__": False}
    step = 0
    start_time = time.time()
    while not done["__all__"]:
        # time.sleep(0.1)
        if step < 50: # todo: 车道上没有足够的空间来容纳新车（堵车），SUMO会等待直到有足够的空间可供其进入车道
            env._add_truck("v_"+str(step), task = None)
        step += 1
        s, r, done, _ = env.step({})
        if step % 5 ==0:
            env.get_current_vehicles()
    env.close()
    end_time = time.time()
    print(end_time - start_time)








