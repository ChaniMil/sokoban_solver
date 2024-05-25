import subprocess
import os
import time
import csv


def measure_time(command):
    """
    This function runs the board on smv, and measures the time
    :param command: the engine to run on - bdd/sat
    :return: the time it ran
    """
    start_time = time.time()
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    return end_time - start_time  # seconds


def main():
    # Directory containing your models
    model_dir = "C:\\Users\\Owner\\PycharmProjects\\groman\\outputs"
    # Directory where your nuXmv model file is located
    nuxmv_directory = "C:\\Users\\Owner\\OneDrive\\שולחן העבודה\\אימות פורמלי\\proj"
    # Output file for performance results
    output_file = "performance_results.csv"
    # Set your desired BMC length here
    bmc_length = 20

    os.chdir(nuxmv_directory)

    # Open the output file in write mode
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Model", "BDD Time (sec)", "SAT Time (sec)"])

        # Loop through each model in the directory
        for model in os.listdir(model_dir):
            if model.endswith(".smv"):
                model_filename = os.path.join(model_dir, model)
                print(f"Processing model: {model_filename}")

                # Measure BDD performance
                command_bdd = ["nuXmv", model_filename]
                bdd_time = measure_time(command_bdd)

                # Measure SAT performance
                command_sat = ["nuXmv", "-bmc", "-bmc_length", str(bmc_length), model_filename]
                sat_time = measure_time(command_sat)

                # Write results to the CSV file
                writer.writerow([model, bdd_time, sat_time])

    print(f"Performance measurement completed. Results are in {output_file}")


if __name__ == "__main__":
    main()
