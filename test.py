import json
import io
from snap_pycrsctl import CrsctlCollector

coll = CrsctlCollector("crsctl-py", 1)
config = json.load(io.open('config_2.json'))
metrics = coll.update_catalog(config)
print(metrics)
print("="*30)

metrics[0]._config = config

metricscoll = coll.collect(metrics)
print(metricscoll)