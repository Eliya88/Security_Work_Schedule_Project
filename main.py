from SecurityDepartment import SecurityDepartment
import time


# Do the work arrangement to be posted at:
#

if __name__ == '__main__':
    start_time = time.time()

    # Dictionary to store arrangements and their accuracy scores
    optimal = {}

    # Create a SecurityDepartment object
    department = SecurityDepartment()

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

    # Post the optimal arrangement
    department.post_arrangement(optimal[max(optimal)])

    end_time = time.time()
    print(end_time - start_time)  # Debugging Purpose
