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
    truck_id = 0
    while not done["__all__"]:
        time.sleep(0.1)
        env._add_truck(str(truck_id)+"ns", "route_ns")
        time.sleep(0.05)
        env._add_truck(str(truck_id)+"we", "route_we")
        truck_id += 1
        s, r, done, _ = env.step({})
        env.get_current_vehicles()

    env.close()







