from snap_pycrsctl import CrsctlCollector


def run():
    version = 1
    CrsctlCollector("crsctl-py", int(version)).start_plugin()

if __name__ == "__main__":
    run()
