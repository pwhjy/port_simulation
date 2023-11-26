import argparse
import os
import sys
from datetime import datetime


if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")


from sumo_rl import SumoEnvironment
from sumo_rl.agents import QLAgent
from sumo_rl.exploration import EpsilonGreedy


if __name__ == "__main__":
    prs = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="""Q-Learning Single-Intersection""" )
    prs.add_argument(
        "-route",
        dest="route",
        type=str,
        default="nets/single-intersection/single-intersection.rou.xml",
        # default="nets/double/flow.rou.xml",
        # default="nets/4x4-Lucas/4x4c1c2c1c2.rou.xml",
        help="Route definition xml file.\n",
    )
    prs.add_argument(
        "-nets",
        dest="nets",
        type=str,
        # default="nets/double/network.net.xml",
        default="nets/single-intersection/single-intersection.net.xml",
        # default="nets/4x4-Lucas/4x4.net.xml",
        help="Nets definition xml file.\n",
    )

    prs.add_argument("-me", dest="min_epsilon", type=float, default=0.005, required=False, help="Minimum epsilon.\n")
    prs.add_argument("-mingreen", dest="min_green", type=int, default=10, required=False, help="Minimum green time.\n")
    prs.add_argument("-maxgreen", dest="max_green", type=int, default=50, required=False, help="Maximum green time.\n")
    prs.add_argument("-gui", action="store_true", default=True, help="Run with visualization on SUMO.\n")
    prs.add_argument("-ns", dest="ns", type=int, default=42, required=False, help="Fixed green time for NS.\n")
    prs.add_argument("-we", dest="we", type=int, default=42, required=False, help="Fixed green time for WE.\n")
    prs.add_argument("-s", dest="seconds", type=int, default=100000, required=False, help="Number of simulation seconds.\n")
    prs.add_argument("-v", action="store_true", default=False, help="Print experience tuple.\n")
    args = prs.parse_args()

    experiment_time = str(datetime.now()).split(".")[0]
    import re
    experiment_time = re.sub(":", "_", experiment_time)
    out_csv = f"outputs/single-intersection"

    env = SumoEnvironment(
        net_file=args.nets,
        route_file=args.route,
        out_csv_name=out_csv,
        use_gui=args.gui,
        num_seconds=args.seconds,
        min_green=args.min_green,
        max_green=args.max_green,
    )
    initial_states = env.reset()
    done = {"__all__": False}
    while not done["__all__"]:
        s, r, done, _ = env.step(action={})
        env._get_current_vehicles()
    env.save_csv(out_csv, episode = 1)
    env.close()







