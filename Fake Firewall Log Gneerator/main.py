import time, random

ACTIONS = ["ALLOW", "DENY"]
PROTOCOLS = ["TCP", "UDP"]
IPS = ["192.168.0.1", "10.0.0.2", "172.16.0.3", "8.8.8.8"]

while True:
    line = f"{random.choice(ACTIONS)} {random.choice(PROTOCOLS)} {random.choice(IPS)}:{random.randint(1000,9999)} -> {random.choice(IPS)}:{random.randint(1000,9999)}\n"
    with open("firewall.log", "a") as f:
        f.write(line)
    time.sleep(2)
