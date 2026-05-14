"""
Generate Algorithm Report
Run this script to display the comprehensive algorithm report for the project
"""

from report_generator import AlgorithmReport


def main():
    print("Generating Algorithm Report for PAC-MAN Game Project...\n")

    # Display the report
    AlgorithmReport.print_report()
    AlgorithmReport.save_report("algorithm_report.txt")
    print("\nReport saved to algorithm_report.txt")


if __name__ == "__main__":
    main()
