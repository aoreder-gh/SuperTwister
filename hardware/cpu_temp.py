# ==============================================================
# Super Twister 3001
# cpu_temp function to get CPU temperature on Raspberry Pi
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================  

import subprocess
import state
from utils.debug import dprint

# ================= CPU TEMP =================
def cpu_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp_raw = int(f.read().strip())
        temp = temp_raw / 1000.0
        try:    
            result = subprocess.run(['/usr/bin/vcgencmd', 'measure_temp'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                output = result.stdout.strip()
                if output.startswith('temp=') and output.endswith("'C"):
                    temp_vcg = float(output[5:-2])
                    temp = max(temp, temp_vcg)
                    state.cpu_temp = int(temp)
                    dprint(f"CPU-Temperatur: {temp} °C")
        except subprocess.TimeoutExpired:
            state.cpu_temp = "N/A timeout"
            dprint("vcgencmd timeout")
        except Exception as e:
            state.cpu_temp = "N/A error"
            dprint(f"Error at vcgencmd: {e}")