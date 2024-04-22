from SecurityDepartment import SecurityDepartment
import time

if __name__ == '__main__':
    start_time = time.time()

    # Start the proces
    department = SecurityDepartment()

    # Do the work arrangement
    department.do_work_arrangement()

    end_time = time.time()
    run_time = end_time - start_time
    print(run_time)
