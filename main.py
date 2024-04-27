from SecurityDepartment import SecurityDepartment
import time


def get_optimal(department):
    # Dictionary to store arrangements and their accuracy scores
    optimal = {}

    # Run the work arrangement N times and store the optimal arrangement
    for i in range(50):
        # Reset the data structure and count the shifts
        department.reset_data_structure()
        department.count_shifts()

        # Do the work arrangement, return the arrangement, the amount of employees that are short,
        # and the number of warnings
        arrangement, emp_shortness_amount, warnings_amount = department.do_work_arrangement()

        # Calculate the accuracy of the arrangement
        accuracy_1 = 1 - (emp_shortness_amount / 100)
        accuracy_2 = (21 - warnings_amount) / 21

        # Store the arrangement and its accuracy
        optimal[round(accuracy_1, 3), round(accuracy_2, 3)] = arrangement

    print(optimal.keys())  # Debugging Purpose
    # Get the arrangement with the highest accuracy score
    max_key = max(optimal.keys(), key=lambda x: x[0] + x[1])
    print(max_key)  # Debugging Purpose

    return optimal[max_key]


if __name__ == '__main__':
    start_time = time.time()

    # Create a SecurityDepartment object
    security_department = SecurityDepartment()

    optimal_arrangement = get_optimal(security_department)

    # Post the optimal arrangement
    security_department.post_arrangement(optimal_arrangement)

    end_time = time.time()
    print(end_time - start_time)  # Debugging Purpose
