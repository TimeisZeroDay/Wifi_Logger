import argparse
import os
import re
import subprocess
import time
import datetime

FIELD_MAP = {
    "ssid": "SSID",
    "signal": "Signal",
    "rx_rate": "Receive rate (Mbps)",
    "tx_rate": "Transmit rate (Mbps)",
    "channel": "Channel",
    "state": "State",
    "bssid": "BSSID",
    "radio": "Radio type",
}


def run_netsh_interfaces() -> str:
    cp = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    return cp.stdout


def parse_netsh_kv(text: str) -> dict:
    data = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        key = left.strip()
        value = right.strip()
        data[key] = value
    return data


def to_float_mbps(v: str):
    try:
        return float(v)
    except Exception:
        return None


def to_int_channel(v: str):
    try:
        return int(v)
    except Exception:
        return None


def to_int_percent(v: str):
    m = re.match(r"^\s*(\d+)\s*%\s*$", v or "")
    return int(m.group(1)) if m else None


def collect_sample() -> dict:
    raw = run_netsh_interfaces()
    kv = parse_netsh_kv(raw)

    return {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "state": kv.get(FIELD_MAP["state"]),
        "ssid": kv.get(FIELD_MAP["ssid"]),
        "bssid": kv.get(FIELD_MAP["bssid"]),
        "signal_percent": to_int_percent(kv.get(FIELD_MAP["signal"], "")),
        "rx_mbps": to_float_mbps(kv.get(FIELD_MAP["rx_rate"], "")),
        "tx_mbps": to_float_mbps(kv.get(FIELD_MAP["tx_rate"], "")),
        "channel": to_int_channel(kv.get(FIELD_MAP["channel"], "")),
        "radio_type": kv.get(FIELD_MAP["radio"]),
    }


def append_txt(path: str, row: dict):
    # this creates the file if it dont exist alr
    line = (
        f'{row["timestamp"]} | '
        f'SSID={row["ssid"]} | '
        f'Signal={row["signal_percent"]}% | '
        f'RX={row["rx_mbps"]} Mbps | '
        f'TX={row["tx_mbps"]} Mbps | '
        f'Ch={row["channel"]} | '
        f'State={row["state"]} | '
        f'Radio={row["radio_type"]} | '
        f'BSSID={row["bssid"]}'
    )
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def main():
    p = argparse.ArgumentParser(description="Log Wi-Fi stats using netsh to a Notepad-friendly TXT.")
    p.add_argument("--interval", type=int, default=60, help="Seconds between samples (default: 60).")
    p.add_argument("--out", default="wifi_log.txt", help="Output TXT path (default: wifi_log.txt).")
    p.add_argument("--print", dest="do_print", action="store_true", help="Print each sample to console.")
    p.add_argument("--open-notepad", action="store_true", help="Open the output file in Notepad.")
    args = p.parse_args()

    out_path = os.path.abspath(args.out)

    if args.open_notepad:
        subprocess.Popen(["notepad.exe", out_path])  # Opens notepad

    while True:
        row = collect_sample()
        append_txt(out_path, row)

        if args.do_print:
            print(row)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
datetime.datetime.now()
