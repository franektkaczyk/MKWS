
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def read_scalar_field(path):
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None

    n_values, start_idx = None, None
    for i, line in enumerate(lines):
        if 'nonuniform' in line and 'List<scalar>' in line:
            try:
                n_values = int(lines[i + 1].strip())
                start_idx = i + 3
                break
            except ValueError:
                continue

    if start_idx is None or n_values is None:
        return None

    values = []
    for line in lines[start_idx:]:
        if ')' in line:
            break
        stripped = line.strip().strip(';')
        if stripped:
            try:
                values.append(float(stripped))
            except ValueError:
                continue

    if len(values) != n_values:
        return None

    return np.array(values)

def analyze_series(case_dir):
    times = []
    t_max_list = []
    rho_min_list = []
    rho_max_list = []
    p_max_list = []
    p_avg_list = []

    time_dirs = []
    for d in os.listdir(case_dir):
        path = os.path.join(case_dir, d)
        if os.path.isdir(path):
            try:
                t_val = float(d)
                if t_val > 0.0:
                    time_dirs.append(d)
            except ValueError:
                continue

    for time_dir in tqdm(sorted(time_dirs, key=float), desc="Processing steps"):
        time_path = os.path.join(case_dir, time_dir)

        t_field = read_scalar_field(os.path.join(time_path, 'T'))
        rho_field = read_scalar_field(os.path.join(time_path, 'rho'))
        p_field = read_scalar_field(os.path.join(time_path, 'p'))

        if t_field is None or rho_field is None or p_field is None:
            continue

        times.append(float(time_dir))
        t_max_list.append(np.max(t_field))
        rho_min_list.append(np.min(rho_field))
        rho_max_list.append(np.max(rho_field))
        p_max_list.append(np.max(p_field))
        p_avg_list.append(np.mean(p_field))

    return (np.array(times), np.array(t_max_list), np.array(rho_min_list),
            np.array(rho_max_list), np.array(p_max_list), np.array(p_avg_list))

def plot_results(times, t_max, rho_min, rho_max, p_max, p_avg, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure()
    plt.plot(times, t_max, label='Max Temperature')
    plt.xlabel('Time [s]')
    plt.ylabel('Temperature [K]')
    plt.title('Maximum Temperature Over Time')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Tmax_vs_time.png'))

    plt.figure()
    plt.plot(times, rho_min, label='Minimum Density', color='green')
    plt.plot(times, rho_max, label='Maximum Density', color='red')
    plt.xlabel('Time [s]')
    plt.ylabel('Density [kg/m³]')
    plt.title('Density Extremes Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rho_min_max_vs_time.png'))

    plt.figure()
    plt.plot(times, p_max, label='Maximum Pressure', color='purple')
    plt.plot(times, p_avg, label='Average Pressure', color='orange')
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure [Pa]')
    plt.title('Pressure Evolution Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pressure_over_time.png'))

    plt.close('all')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_combustion_results.py <case_directory>")
        sys.exit(1)

    case_dir = sys.argv[1]
    output_dir = os.path.join(case_dir, "plots")

    times, t_max, rho_min, rho_max, p_max, p_avg = analyze_series(case_dir)
    plot_results(times, t_max, rho_min, rho_max, p_max, p_avg, output_dir)
