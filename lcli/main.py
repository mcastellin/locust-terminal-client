import json
import os
import re
import signal
import time

import click
import plotille as plt
from bs4 import BeautifulSoup

from .driver import LocustPageDriver


def parse_html_data(html: str) -> dict:
    stat_name = "var stats_history ="
    pattern = r"\.map\(.*\)"
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.findAll("script")

    for script in scripts:
        script_contents = script.string
        if script_contents and "var stats_history" in script_contents:
            stats = script_contents.strip().split(stat_name)[1].strip()
            stats = re.sub(pattern, "", stats)
            return json.loads("".join(stats[:-1].rsplit(",", 1)))

    raise ValueError("Could not find stats history in locust homepage")


def unwrap(point):
    return point.get("value")


def plot(driver, show_legend=False, num_charts=3):
    stats_history = parse_html_data(driver.locust_index())
    ter_size = os.get_terminal_size()
    col_size = min(ter_size.columns - 23, 160)
    row_size = int((ter_size.lines - 3 * num_charts) / num_charts)

    timestamps = stats_history.get("time")
    current_rps = list(map(unwrap, stats_history.get("current_rps")))
    current_err = list(map(unwrap, stats_history.get("current_fail_per_sec")))
    user_count = list(map(unwrap, stats_history.get("user_count")))
    avg_latency = list(map(unwrap, stats_history.get("response_time_percentile_50")))
    p95_latency = list(map(unwrap, stats_history.get("response_time_percentile_95")))
    num_points = len(timestamps)
    X = range(num_points)

    if num_points < 2:
        return "Not enough data"

    out = ["\n\n\n\n\n\n\n\n"]

    fig = plt.Figure()
    fig.width = col_size
    fig.height = row_size
    fig.color_mode = "byte"
    fig.set_x_limits(min_=0, max_=num_points)
    fig.set_y_limits(min_=0, max_=max(current_rps + current_err) + 1)
    fig.plot(X, current_rps, lc=25, label="Current Rps")
    fig.plot(X, current_err, lc=1, label="Current Errors")
    out.append(str(fig.show(legend=show_legend)))

    fig = plt.Figure()
    fig.width = col_size
    fig.height = row_size
    fig.color_mode = "byte"
    fig.set_x_limits(min_=0, max_=num_points)
    fig.set_y_limits(min_=0, max_=max(avg_latency + p95_latency) + 1)
    fig.plot(X, avg_latency, lc=2, label="Avg Latency")
    fig.plot(X, p95_latency, lc=3, label="p95 Latency")
    out.append(str(fig.show(legend=show_legend)))

    fig = plt.Figure()
    fig.width = col_size
    fig.height = row_size - 3
    fig.color_mode = "byte"
    fig.set_x_limits(min_=0, max_=num_points)
    fig.set_y_limits(min_=0, max_=max(user_count) + 1)
    fig.plot(X, user_count, lc=25, label="Users")
    out.append(str(fig.show(legend=show_legend)))
    return "\n".join(out)


class GracefulTermination:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.graceful_termination)
        signal.signal(signal.SIGTERM, self.graceful_termination)

    def graceful_termination(self, *args):
        print(" Exiting..")
        self.kill_now = True


@click.group()
def cli():
    pass


@cli.command()
@click.option("-h", "--host", default="http://localhost:8089", type=click.STRING, help="The locust base URL")
def watch(host):
    handler = GracefulTermination()
    driver = LocustPageDriver(host=host)
    while not handler.kill_now:
        print(plot(driver))
        time.sleep(3)


if __name__ == "__main__":
    cli()
