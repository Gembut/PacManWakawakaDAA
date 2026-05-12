"""
Generate Algorithm Report
Run this script to display the comprehensive algorithm report for the project
"""

from report_generator import AlgorithmReport


def main():
    print("Generating Algorithm Report for PAC-MAN Game Project...\n")

    # Display the report
    AlgorithmReport.print_report()

    # Save to file
    filename = AlgorithmReport.save_report("algorithm_report.txt")
    print(f"\n✓ Report saved to: {filename}")

    # Save CSV version
    csv_content = AlgorithmReport.generate_csv_report()
    with open("algorithm_metrics.csv", "w") as f:
        f.write(csv_content)
    print("✓ CSV metrics saved to: algorithm_metrics.csv")


if __name__ == "__main__":
    main()
