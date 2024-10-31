import json
import subprocess

import matplotlib.pyplot as plt


def run_performance_test(users, seconds):
    bash_command = f"locust -f locustfile.py --headless -u {users} -r {users} --host=http://127.0.0.1:5000 --run-time {seconds}s --json"
    try:
        result = subprocess.run(bash_command, shell=True, capture_output=True, text=True, check=True)
        stdout = result.stdout
        performance = json.loads(stdout)
        return performance
    except subprocess.CalledProcessError as e:
        print(f"Error running performance test: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}")
        print(f"Raw output: {stdout}")
        return None

def get_avg_metric(performance, name):
    total_response_time = 0
    num_requests = 0

    specific_entries = [entry for entry in performance if entry["name"] == name]
    for entry in specific_entries:
        num_requests += entry["num_requests"]
        total_response_time += entry["total_response_time"]

    result = 0
    if num_requests > 0:
        result = total_response_time / num_requests

    return result

def plot_performance_metrics(performances, user_counts):
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.tight_layout()

    scenarios = ["register", "login", "refresh", "logout", "add_smart_meter", "get_smart_meters",
                 "get_smart_meter_by_id", "update_smart_meter", "add_metadata"]
    for scenario in scenarios:
        data = []
        for performance in performances:
            value = int(get_avg_metric(performance, scenario))
            data.append(value)
        ax.plot(data, label=scenario)

    ax.set_xticks(range(len(user_counts)))
    ax.set_xticklabels(user_counts)
    ax.set_xlabel('Number of users')
    ax.set_ylabel('Max response time')
    ax.set_title('Performance Metrics')
    ax.legend()
    plt.savefig(f"./performance.pdf", transparent=True)
    plt.show()


if __name__ == "__main__":
    duration_in_seconds = 10
    performances = []
    user_counts = [10, 20, 50, 100, 200, 400, 500]

    print("Performance test started")
    for count in user_counts:
        performances.append(run_performance_test(count, duration_in_seconds))
    print("Performance test ended")

    plot_performance_metrics(performances, user_counts)
