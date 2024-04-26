from SecurityDepartment import SecurityDepartment
import time

if __name__ == '__main__':
    start_time = time.time()

    # Set the security department
    department = SecurityDepartment()

    # Do the work arrangement to be posted at:
    # 'https://docs.google.com/spreadsheets/d/1gmsseO5a7PZqAWLaNdVcHx75z9TsiSvcx9u-JtiCh_0/edit#gid=0'
    department.do_work_arrangement()

    end_time = time.time()
    run_time = end_time - start_time
    print(run_time)
