---
title: Reward
firstpage:
---

## Reward

The default reward function is the change in cumulative vehicle delay:



It is also possible to implement your own reward function:

```python
def my_reward_fn(traffic_signal):
    return traffic_signal.get_average_speed()

env = SumoEnvironment(..., reward_fn=my_reward_fn)
```
