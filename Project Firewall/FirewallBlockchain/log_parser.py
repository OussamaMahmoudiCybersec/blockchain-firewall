import time
import os
import django
import re

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FirewallBlockchain.settings')  # <-- CHANGE THIS
django.setup()

from logs.models import FirewallLog  # <-- Make sure app is named 'logs'

# Log file to monitor
log_file_path = r'C:\Users\Moonlight\Downloads\PFE\Fake Firewall Log Gneerator\firewall.log'

# Regex pattern: e.g., ALLOW TCP 10.0.0.2:6263 -> 172.16.0.3:1015
log_pattern = re.compile(r'^(ALLOW|DENY)\s+(TCP|UDP)\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+->\s+(\d+\.\d+\.\d+\.\d+):(\d+)$')

print(f"📡 Monitoring {log_file_path} for changes...")

def tail_log():
    with open(log_file_path, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            line = line.strip()
            match = log_pattern.match(line)
            if match:
                action, protocol, src_ip, src_port, dst_ip, dst_port = match.groups()
                try:
                    FirewallLog.objects.create(
                        action=action,
                        protocol=protocol,
                        source_ip=src_ip,
                        source_port=int(src_port),
                        destination_ip=dst_ip,
                        destination_port=int(dst_port)
                    )
                    print(f"✅ Inserted: {line}")
                except Exception as e:
                    print(f"✅ Inserted:: {e}")
            else:
                print(f"⚠️ Unrecognized format: {line}")

if __name__ == '__main__':
    tail_log()
