import sys
from Association.TrafficBureau import Queuer
# Cooperate with bash in terminal
machine_ip = sys.argv[1]
Supervisor = Queuer()
Supervisor.QueueCleaner(machine_ip)
