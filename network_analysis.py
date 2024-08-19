import logging
from fastapi import FastAPI, Query
import speedtest
import psutil
import subprocess
import nmap
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

def parse_iperf_output(output):
    lines = output.strip().splitlines()
    cleaned_output = {
        "connection_info": "",
        "test_results": [],
        "summary": {}
    }

    try:
        # Find and store the connection info
        for line in lines:
            if "Connecting to host" in line:
                cleaned_output["connection_info"] = line
                break
        
        # Parse each line for results
        for line in lines:
            if "[ ID]" in line and "Interval" in line:
                continue  # Skip the header line
            if line.startswith("[  "):
                parts = line.split()
                if len(parts) >= 9 and parts[2].count('-') == 1:
                    cleaned_output["test_results"].append({
                        "interval": parts[2],
                        "transfer": f"{parts[4]} {parts[5]}",
                        "bandwidth": f"{parts[6]} {parts[7]}"
                    })
        
        # Parse the summary results at the end
        for line in lines:
            if "sender" in line or "receiver" in line:
                summary_parts = line.split()
                if len(summary_parts) >= 9:
                    cleaned_output["summary"] = {
                        "total_transfer": f"{summary_parts[4]} {summary_parts[5]}",
                        "average_bandwidth": f"{summary_parts[6]} {summary_parts[7]}"
                    }

    except IndexError:
        cleaned_output["error"] = "Unexpected output format"

    return cleaned_output

def parse_packet_loss(output):
    lines = output.strip().splitlines()
    packet_loss_info = {
        "datagrams_sent": None,
        "datagrams_received": None,
        "lost_datagrams": None,
        "loss_percentage": None
    }

    try:
        for line in lines:
            if "datagrams received" in line:
                parts = line.split()
                if len(parts) >= 11:
                    packet_loss_info = {
                        "datagrams_sent": parts[3],
                        "datagrams_received": parts[5],
                        "lost_datagrams": parts[8],
                        "loss_percentage": parts[10].strip("()%")
                    }
                break

    except IndexError:
        packet_loss_info["error"] = "Unexpected output format"

    return packet_loss_info

def run_packet_loss_test(server='127.0.0.1', duration=10, bandwidth='10M'):
    command = ["iperf3", "-c", server, "-u", "-t", str(duration), "-b", bandwidth]
    result = subprocess.run(command, capture_output=True, text=True)
    return parse_packet_loss(result.stdout)

def get_network_info():
    logging.info("Starting network interface information retrieval.")
    network_info = psutil.net_if_addrs()
    network_stats = psutil.net_if_stats()
    interfaces = {}
    for iface_name, iface_addresses in network_info.items():
        if iface_name in network_stats:
            interfaces[iface_name] = {
                "is_up": network_stats[iface_name].isup,
                "speed": f"{network_stats[iface_name].speed} Mbps",
                "duplex": network_stats[iface_name].duplex,
                "mtu": network_stats[iface_name].mtu
            }
    logging.info("Completed network interface information retrieval.")
    return interfaces

def ping_test(hostname):
    logging.info(f"Starting ping test to {hostname}.")
    try:
        output = subprocess.run(["ping", "-n", "4", hostname], capture_output=True, text=True)
        logging.info(f"Completed ping test to {hostname}.")
        return output.stdout
    except Exception as e:
        logging.error(f"Ping test to {hostname} failed: {e}")
        return str(e)

def scan_network():
    logging.info("Starting network scan.")
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-sn')  # Adjust the subnet to match your network
    devices = []
    for host in nm.all_hosts():
        if 'mac' in nm[host]['addresses']:
            devices.append({
                "ip": nm[host]['addresses']['ipv4'],
                "mac": nm[host]['addresses']['mac'],
                "hostname": nm[host].hostname(),
                "status": nm[host].state()
            })
        else:
            devices.append({
                "ip": nm[host]['addresses']['ipv4'],
                "hostname": nm[host].hostname(),
                "status": nm[host].state()
            })
    logging.info("Completed network scan.")
    return devices

def run_speedtest():
    logging.info("Starting speed test.")
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    ping = st.results.ping
    logging.info("Completed speed test.")
    return {
        "download_speed": f"{download_speed:.2f} Mbps",
        "upload_speed": f"{upload_speed:.2f} Mbps",
        "ping": f"{ping} ms"
    }

def run_stress_test(server='127.0.0.1', duration=2, parallel_streams=25, udp=False, bandwidth="10G"):
    logging.info("Starting maximum network stress test.")
    try:
        command = ["iperf3", "-c", server, "-t", str(duration), "-P", str(parallel_streams)]
        
        if udp:
            command.append("-u")  # Use UDP
            command.append("-b")
            command.append(bandwidth)  # Set high bandwidth for UDP

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        logging.info("Completed maximum network stress test.")
        return parse_iperf_output(result.stdout)
    except FileNotFoundError:
        logging.error("iperf3 is not installed or not found in PATH.")
        return {"error": "iperf3 not found"}
    except Exception as e:
        logging.error(f"Stress test failed: {e}")
        return {"error": str(e)}


@app.get("/run_tests")
def run_tests(
    run_speed: bool = Query(True, description="Run speed test"),
    run_diagnostics: bool = Query(True, description="Run network diagnostics"),
    run_scan: bool = Query(True, description="Run network scan"),
    run_stress: bool = Query(True, description="Run network stress test"),
    run_packet_loss: bool = Query(False, description="Run packet loss test")  # Default to False
):
    logging.info("Initiating selected tests.")
    results = {}

    with ThreadPoolExecutor() as executor:
        futures = []

        if run_speed:
            futures.append(("speedtest", executor.submit(run_speedtest)))
        
        if run_diagnostics:
            futures.append(("network_diagnostics", executor.submit(run_diagnostics)))
        
        if run_scan:
            futures.append(("connected_devices", executor.submit(scan_network)))
        
        if run_stress:
            futures.append(("stress_test", executor.submit(run_stress_test)))

        if run_packet_loss:
            futures.append(("packet_loss", executor.submit(run_packet_loss_test)))

        for name, future in futures:
            results[name] = future.result()

    logging.info("Selected tests completed successfully.")
    return results

def run_diagnostics():
    logging.info("Starting network diagnostics.")
    network_info = get_network_info()
    ping_google = ping_test("8.8.8.8")
    ping_cloudflare = ping_test("1.1.1.1")

    logging.info("Completed network diagnostics.")
    return {
        "network_info": network_info,
        "ping_google": ping_google,
        "ping_cloudflare": ping_cloudflare
    }

if __name__ == "__main__":
    logging.info("Starting FastAPI application.")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
