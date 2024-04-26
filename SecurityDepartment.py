import pandas as pd
import SecurityGuard
import requests
import heapq
import os
from random import shuffle


def check_shift(employee, day, shift):
    """ This method check if the employee worked in the given day and shift.
     :return : 'X' If he worked to be put in Google sheets.
     :return : '' If he didn't work to be put in Google sheets.
     """
    if employee.get_shift(day, shift):
        return 'X'
    return ""


def day_name(day):
    """
    Convert the day number to the day name.
    :param day: The day in number
    :return: The day name
    """
    days_dict = {0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday'}
    return days_dict[day]


def shift_name(shift):
    """
    Convert the shift number to the shift name.
    :param shift: The shift in number
    :return: The shift name
    """
    shifts_dict = {0: 'Morning', 1: 'Evening', 2: 'Night'}
    return shifts_dict[shift]


class SecurityDepartment:
    """
    Represents the security department in the company.
    """

    def __init__(self):
        """ This class is responsible for the security department.
            It contains all the information about the department and how to make a work arrangement """
        # permanent fields
        self.MAX_SHIFTS = 6
        self.MAX_NIGHTS_SHIFTS = 7
        self.MAX_SHABAT_SHIFTS = 3
        self.MAX_EMPLOYEE_PER_SHIFT = 5
        # Environment variables for the API
        self.ENDPOINT_GET_DATA = os.getenv('ENDPOINT_GET')
        self.TOKEN_GET = os.getenv('TOKEN_GET')
        self.ENDPOINT_UPLOAD_DATA = os.getenv('ENDPOINT_PUT')
        self.TOKEN_PUT = os.getenv('TOKEN_PUT')

        # Set of all the guards in the department, initialized in the method 'set_guards_objects_list'
        self.guards_objects_list = set()

        # Number of employees per shift. Initialized in the method 'count_shifts'
        self.employee_amount_in_shift = []
        self.employee_amount_in_shift_noon = []

        # Collect all information from Google sheets data, store it by shifts,
        # each set contains the employees in the shift.
        self.dict_of_shifts = {day: (set(), set(), set()) for day in range(7)}

        # The final arrangement of the shifts
        self.final_arrangement = {day: (set(), set(), set()) for day in range(7)}

        # The warning output of the shifts
        self.warning_output = {day: (set(), set(), set()) for day in range(7)}

        try:
            # Read the data from Google sheets using Sheety API
            response = requests.get(url=self.ENDPOINT_GET_DATA,
                                    headers={"Authorization": f"Bearer {self.TOKEN_GET}"})
            response.raise_for_status()
            self.data = response.json()
            response.close()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"Error: {e}")

        # Set the attributes of the guards
        self.set_guards_objects_list()
        self.set_data()
        # self.count_shifts()

    def reset_data_structure(self):
        """
        Reset the data structure to the initial state.
        """
        self.employee_amount_in_shift = []
        self.employee_amount_in_shift_noon = []
        self.final_arrangement = {day: (set(), set(), set()) for day in range(7)}
        self.warning_output = {day: (set(), set(), set()) for day in range(7)}

        # Reset all employees shifts
        for employee in self.guards_objects_list:
            employee.reset_all_shifts()

    def set_guards_objects_list(self):
        """
            Make a list of all the guards in the department from the CSV file.
            Each guard is an object of the class 'SecurityGuard'.
        """
        # Load data of all employees in the department into Pandas DataFrame from the CSV file
        try:
            df = pd.read_csv('employee_data.csv')
        except FileNotFoundError:
            raise FileNotFoundError("The file 'employee_data.csv' was not found.")

        # Create a list of objects with the guards in the department
        for i in range(len(df)):
            self.guards_objects_list.add(
                SecurityGuard.SecurityGuard(
                    name=str(df['E_Name'].iloc[i]).strip(),
                    id_number=int(df['eID'].iloc[i]),
                    is_officer=bool(df['Is_Officer'].iloc[i]),
                    has_height_permission=bool(df['Has_Height'].iloc[i]),
                    can_drive=bool(df['Can_Drive'].iloc[i]),
                    shabat_counter=int(df['Shabat_Count'].iloc[i]),
                    nights_counter=int(df['Nights_Count'].iloc[i]),
                    work_shabat_night=bool(df['Shabat_Night'].iloc[i])
                )
            )

    def set_data(self):
        """
            Collect all information from 'sheets' input data,
            and store in each shift in the week, all the employee that marks the shift.
            This will help to arrange the shifts by the number of employees in each shift.
        """
        # Initial the dictionary shifts
        for i in range(1, len(self.guards_objects_list) + 2):  # The first row is the title
            employee = None
            for obj in self.guards_objects_list:
                if obj.get_name() == self.data['security'][i]["שם"]:  # The name of the employee in the sheets document
                    employee = obj
                    # print(employee.get_name())
                    break
            # The employee is not in the sheets document so continue to the next employee
            if employee is None:
                continue

            count = -1  # -1 to skip the first value (name)

            # Iterate over the row of the employee in the sheets document to get the shifts and the number of shifts.
            for val in self.data['security'][i].values():
                # The first iteration is the title
                if count == -1:
                    count += 1
                    continue

                day = count // 3  # Sunday is 0 and so on
                shift = count % 3  # Morning is 0 and so on

                # The employee opens the shift
                if val != '' and type(val) is not int:  # We expected an 'X' or an empty string
                    # Add the employee to the dictionary by day and shift
                    self.dict_of_shifts[day][shift].add(employee)

                # Set how many shifts the employee want to work this week
                elif type(val) is int and 0 <= val <= 6:
                    employee.set_optimal_num_of_shifts(val)
                    break
                count += 1

    def count_shifts(self):
        """
         Set the attribute employee_amount_in_shift by the number of employees in each shift.
        """
        for day, value in self.dict_of_shifts.items():
            for shift in range(3):
                if shift == 0 or shift == 2:
                    self.employee_amount_in_shift.append((len(value[shift]), day, shift))
                elif shift == 1:
                    self.employee_amount_in_shift_noon.append((len(value[shift]), day, shift))

        # Transform the list to a heap queue to find the minimum value in a more efficient way.
        heapq.heapify(self.employee_amount_in_shift)
        heapq.heapify(self.employee_amount_in_shift_noon)

    def find_min_shift(self, num):
        """
         Find the day and shift with the minimum number of employees to start the work arrangement.
        :return: Day, shift, min_employee_amount, day_in_num
        """
        day, shift, min_employee_amount = 0, 0, 0
        # Get the shift with the minimum number of employees
        if num % 3 == 0 or num % 3 == 1:
            min_employee_amount, day, shift = heapq.heappop(self.employee_amount_in_shift)

        elif num % 3 == 2:
            min_employee_amount, day, shift = heapq.heappop(self.employee_amount_in_shift_noon)

        return day, shift, min_employee_amount

    def do_work_arrangement(self):
        """
        Do the work arrangement, the main function of the class.
        Iterate over all the shifts by the number of employees in the shift from the minimum to the maximum.
        We need:
        1. At least one officer in the shift.
        2. At least two drivers in the shift.
        3. At least two employees with height permission in the shift.
        4. The employee can't work in the shift if he worked in the previous shift.
        """
        # Each iteration we complete one shift
        idx_of_shift = 0
        while idx_of_shift < 21:
            min_shift = self.find_min_shift(idx_of_shift)
            day = min_shift[0]
            shift = min_shift[1]
            num_of_employee = min_shift[2]
            can_work_list = [[], []]  # [officers, guards]

            employye_list = list(self.dict_of_shifts[day][shift])
            for i in range(num_of_employee):
                employee = employye_list[i]

                if self.filter_employees(employee, day, shift) is False:
                    continue

                # Add the employee to the list of employees that can work
                if employee.is_officer():
                    can_work_list[0].append(employee)
                else:
                    can_work_list[1].append(employee)

            # Assign the shift and get the warning output
            warning = self.assign_shift(can_work_list, day, shift)
            if warning is not None:
                self.warning_output[day][shift].add(warning)
            else:
                self.warning_output[day][shift].add("")

            # Update the number of shifts
            idx_of_shift += 1

        # self.optimize_assignment()
        # self.update_csv_file()
        return self.ready_arrangment()

    def post_arrangement(self, updates: dict):
        """
        Post the final arrangement on Google Sheets and warn about the shifts that are not optimal
        """
        # Batch update to Google Sheets
        try:
            for shift in range(3):
                sheet_params = {
                    'chart1': {
                        'shift': shift_name(shift),
                        'sunday': updates.get((shift, 0)),
                        'monday': updates.get((shift, 1)),
                        'tuesday': updates.get((shift, 2)),
                        'wednesday': updates.get((shift, 3)),
                        'thursday': updates.get((shift, 4)),
                        'friday': updates.get((shift, 5)),
                        'saturday': updates.get((shift, 6))
                    }
                }
                response = requests.put(url=f"{self.ENDPOINT_UPLOAD_DATA}/{shift + 2}", json=sheet_params,
                                        headers={"Authorization": f"Bearer {self.TOKEN_PUT}"})
                response.raise_for_status()
                response.close()

        except requests.exceptions.RequestException as e:
            print(f"Error posting updates: {e}")

    def ready_arrangment(self):
        noon_shortages = {day: self.check_noon_shortage(day) for day in range(7)}  # Pre-compute noon shortages

        # Iterate over all the shifts and days
        updates = {}
        shifts_with_12 = {day: [0, 0, 0] for day in range(7)}  # The number of 12-hour shifts in the shift
        warnings_amount = 0
        employee_shortness = 0

        for shift in [0, 2, 1]:  # Shifts
            for day in range(7):  # Days
                count_12 = 0
                shift_employees = []  # Employyes in the shift to be added
                # Add the employees to the shift
                for employee in self.final_arrangement[day][shift]:
                    name_line = employee.get_name()
                    # Try to fill the noon shift shortage with 12-hour shifts
                    if shift == 0 and employee in noon_shortages[day][0]:  # Morning shift
                        name_line += ' * 12 *'
                        count_12 += 1

                    elif shift == 2 and employee in noon_shortages[day][1]:  # Night shift
                        name_line += ' * 12 *'
                        count_12 += 1
                    shift_employees.append(name_line + '\n')

                # Update the number of 12-hour shifts in the shift
                shifts_with_12[day][shift] = count_12

                # Add the warning output to the shift employees
                if shift == 1:
                    e_in_shift = len(self.final_arrangement[day][1])
                    if (e_in_shift + shifts_with_12[day][0] == 5) and (e_in_shift + shifts_with_12[day][2] == 5):
                        shift_employees.append('')
                    else:
                        shift_employees.append(list(self.warning_output[day][shift])[0])

                elif shift != 1:
                    shift_employees.append(list(self.warning_output[day][shift])[0])

                if list(self.warning_output[day][shift])[0] != '':
                    warnings_amount += 1
                # -----------------------------------------------------
                if shift != 1:
                    employee_shortness += (5 - len(self.final_arrangement[day][shift]))
                if shift == 1:
                    employee_shortness += (5 - len(self.final_arrangement[day][1]) -
                                           min(shifts_with_12[day][0], shifts_with_12[day][2]))
                # -----------------------------------------------------

                # Combine the employees in the shift into a string
                updates[(shift, day)] = ''.join(shift_employees)
        return updates, employee_shortness, warnings_amount

    def filter_employees(self, employee, day, shift):
        """
        Filter the employees that can work in the shift.
        The function assigns the shifts to the employees by the following conditions:
        1. The employee can't work in a morning shift if he worked on the previous day at night.
        2. The employee can't work in a night shift if he works in the next day in the morning.
        :param employee: Employee object
        :param day: The day in number
        :param shift: The shift in number
        :return: True if the employee can work in the shift by the following conditions, False otherwise
        """

        # The employee passed the maximum shabat shifts amount
        shabat_conditions = {(5, 1), (5, 2), (6, 0), (6, 1)}
        if (day, shift) in shabat_conditions:
            if employee.get_shabat_counter() >= self.MAX_SHABAT_SHIFTS:
                return False

        # Morning shift
        if shift == 0:
            # The employee work in shabat night, so he can't work in Sunday morning.
            if day == 0 and employee.is_work_shabat_night():
                return False
            # Need a rest of at least one shift
            if (employee.get_shift(day, 1) or employee.get_shift(day, 2) or
                    (day != 0 and employee.get_shift(day - 1, 2))):
                return False

        # Evening shift
        elif shift == 1:
            # Need a rest of at least one shift
            if employee.get_shift(day, 0) or employee.get_shift(day, 2):
                return False

        # Night shift
        elif shift == 2 and employee.get_nights_counter() < self.MAX_NIGHTS_SHIFTS:
            # Need a rest of at least one shift
            if (employee.get_shift(day, 0) or employee.get_shift(day, 1) or
                    (day != 6 and employee.get_shift(day + 1, 0))):
                return False

        # The employee already has the number of shifts he wants
        if employee.get_num_of_optimal_shifts() == employee.get_num_of_current_shifts():
            return False

        # The employee passed the maximum work hours amount
        if employee.get_num_of_current_shifts() >= self.MAX_SHIFTS:
            return False

        # All the conditions are met
        return True

    def assign_shift(self, employees_list, day, shift):
        """
        Assign to the shift the employees in the list while verifying that: at least one officer,
        at least two drivers and at least two employee with height permission
        :param employees_list: list of employees that can work in the shift
        :param day: the day in number
        :param shift: the shift in number
        :return: warning_output - if the shift is not optimal
        """
        # Sort the employees by the number of optimal shifts they want to work, Shuffle the list before sorting to avoid
        # the same order of the employees as they registered in the sheets document
        shuffle(employees_list[0])
        officers_list = employees_list[0]

        shuffle(employees_list[1])
        guards_list = employees_list[1]

        # The Warning output of the method
        warning_output = ""

        officers_amount = len(officers_list)

        # Assign two officers to the shift if it is possible
        if officers_amount >= 2:
            # Add the officers to the shift in their presonal shift list
            officers_list[0].add_shift(day, shift)
            officers_list[1].add_shift(day, shift)

            # Add the officers to the shift in the final arrangement
            self.final_arrangement[day][shift].add(officers_list[0])
            self.final_arrangement[day][shift].add(officers_list[1])

        # Assign one officer to the shift if it is possible
        elif officers_amount == 1:
            officers_list[0].add_shift(day, shift)
            self.final_arrangement[day][shift].add(officers_list[0])

        # Officers hava drive permission and height permission
        count_drivers = len(self.final_arrangement[day][shift])
        count_height_permissions = len(self.final_arrangement[day][shift])

        # Assign the rest of the employees to the shift, up to 5 employees total.
        for employee in guards_list:
            # Count the number of employees in the shift
            count_shift = len(self.final_arrangement[day][shift])

            # Shabat morning need four employees
            if ((day == 6 and shift == 0 and count_shift == 4) or
                    (count_shift == self.MAX_EMPLOYEE_PER_SHIFT)):
                break

            # Add the employee to the shift
            employee.add_shift(day, shift)
            self.final_arrangement[day][shift].add(employee)

            # Update the counters
            if employee.is_allowed_to_drive():
                count_drivers += 1
            if employee.is_allowed_to_work_on_height():
                count_height_permissions += 1

        # If the shift is not full, try to add more officers
        shortage = self.MAX_EMPLOYEE_PER_SHIFT - len(self.final_arrangement[day][shift])  # The amount of shortage

        # Shabat morning need one less employee
        if day == 6 and shift == 0:
            shortage -= 1

        if shortage > 0:
            # We need to have at least 3 officers in the list, because if we had 2 officers,
            # we would have already added them.
            if officers_amount >= 3:
                condition = min(shortage + 2, officers_amount)
                # Add the officers to the shift in their presonal shift list
                for i in range(2, condition):
                    employee = officers_list[i]
                    employee.add_shift(day, shift)
                    self.final_arrangement[day][shift].add(employee)
                    count_drivers += 1
                    count_height_permissions += 1

        # Check if the shift is optimal
        if officers_amount == 0:
            warning_output += "* No Officers *\n"
            return warning_output

        if day == 6 and shift == 0:
            if len(self.final_arrangement[day][shift]) < 4:
                warning_output += "* Lack of Employees *\n"
                return warning_output
        else:
            if len(self.final_arrangement[day][shift]) < 5:
                warning_output += "* Lack of Employees *\n"
                return warning_output

        if count_drivers < 2:
            warning_output += "* No Enough Drivers *\n"
            return warning_output

        if count_height_permissions < 2:
            warning_output += "* No Enough Height permissions *\n"
            return warning_output

    def update_csv_file(self):
        """ Update the csv file with the new information """
        try:
            df = pd.read_csv('employee_data.csv')
        except FileNotFoundError:
            raise FileNotFoundError("The file 'employee_data.csv' was not found.")

        for employee in self.guards_objects_list:
            # Update the employee info
            df.loc[df['eID'] == employee.get_id_number(), 'Shabat_Count'] = employee.update_shabat_counter()
            df.loc[df['eID'] == employee.get_id_number(), 'Nights_Count'] = employee.count_weekly_nights()
            df.loc[df['eID'] == employee.get_id_number(), 'Shabat_Night'] = int(employee.get_shift(6, 2))

        # Save the new data to the csv file
        df.to_csv('employee_data.csv', index=False)

    def check_noon_shortage(self, day):
        """
        Checks for missing employees in the noon shift and finds replacements from morning and night shifts.
        :param day: The day to check and update the shifts for.
        """
        # Get the noon shift
        noon_shift = self.final_arrangement[day][1]

        # Set the shotage of employees in the noon shift
        missing_count = self.MAX_EMPLOYEE_PER_SHIFT - len(noon_shift)

        # Find potential replacements from morning (0) and night (2) shifts
        replacements = ([], [])  # [morning, night]

        # Check if there are missing employees in the noon shift
        if missing_count > 0:

            # Get the morning and night shifts
            morning_shift = self.final_arrangement[day][0]
            night_shift = self.final_arrangement[day][2]

            # Find replacements from the morning shift
            for employee in morning_shift:
                if len(replacements[0]) < missing_count:
                    if employee in self.dict_of_shifts[day][1]:
                        replacements[0].append(employee)

            # Find replacements from the night shift
            for employee in night_shift:
                if len(replacements[1]) < missing_count:
                    if employee in self.dict_of_shifts[day][1]:
                        replacements[1].append(employee)

        return replacements

    # def optimize_assignment(self):
    #     """
    #     This method optimizes the assignment of the shifts. It finds the employees who didn't get all the shifts they
    #     want and replace them with employees who got the shift they want but can work in another shift.
    #     Algorithm:
    #     1. Iterate over all the employees and find the employee who didn't get all the shifts he wants. (employee_1)
    #     2. Iterate over all the shifts the employee_1 wants, and find a shift that he can work in but didn't get.
    #        - If the shift is not full: continue.
    #        - If the shift is full:
    #             1. Iterate over all the employees in the shift. For each employee, find a shift that
    #             the employee wants
    #                to work in but didn't get.(employee_2)
    #             2. - If the shift is full: continue.
    #                - If the shift is not full:
    #                     1. Remove employee_2 from the original shift.
    #                     2. Add the employee_2 to the new shift.
    #                     3. Add the employee_1 to the original shift.
    #     """
    #     # Iterate over all employeess.
    #     for employee in self.guards_objects_list:
    #
    #         # Find an employee who didn't get the number of shifts he wants's
    #         if employee.get_num_of_current_shifts() < employee.get_num_of_optimal_shifts():
    #
    #             # Iterate over all the shifts, to get the shift the employee wants but didn't get
    #             for day in self.dict_of_shifts.keys():
    #                 for shift in range(3):
    #                     full_shift = self.final_arrangement[day][shift]
    #
    #                     # Check if the employee can work in the shift, and he wants to work in the shift
    #                     if self.optimizer_helper(employee, day, shift, len(full_shift), "equal"):
    #                         print(f"Employee {employee.get_name()} didn't get the shift he wants in"
    #                               f" day {day} shift {shift}")  # Debugging
    #
    #                         employee_to_remove = None
    #                         day_to_append = 0
    #                         shift_to_append = 0
    #                         # Find emplyee in the full shift to replace with the employee who didn't get the shift
    #                         for employee_in_shift in full_shift:
    #
    #                             # Find a shift that the employee can work in but didn't get
    #                             for day1 in self.dict_of_shifts.keys():
    #                                 for shift1 in range(3):
    #                                     full_shift1 = self.final_arrangement[day1][shift1]
    #                                     # Check if the employee can work in the shift, and he wants to work in the shift
    #                                     if self.optimizer_helper(employee_in_shift, day1, shift1, len(full_shift1),
    #                                                              "greater"):
    #                                         print(f"Employee {employee_in_shift.get_name()} can work in day {day1} "
    #                                               f"shift {shift1}")  # Debugging
    #                                         # Save the employee to remove and the day and shift to append
    #                                         employee_to_remove = employee_in_shift
    #                                         day_to_append = day1
    #                                         shift_to_append = shift1
    #                                         break
    #
    #                         # Replace the employees
    #                         if employee_to_remove is not None:
    #                             # Print the replacement for debugging
    #                             print(f"Employee {employee_to_remove.get_name()} is replaced with "
    #                                   f"{employee.get_name()}. from: {day_name(day)}, {shift_name(day)}, to:"
    #                                   f" {day_name(day_to_append)}, {shift_name(shift_to_append)}")
    #
    #                             # Remove the second employee from the original shift
    #                             self.final_arrangement[day][shift].remove(employee_to_remove)
    #                             employee_to_remove.delete_shift(day, shift)
    #
    #                             # Add the second employee to the new shift
    #                             self.final_arrangement[day_to_append][shift_to_append].add(employee_to_remove)
    #                             employee_to_remove.add_shift(day_to_append, shift_to_append)
    #
    #                             # Add the employee to the original shift
    #                             self.final_arrangement[day][shift].add(employee)
    #                             employee.add_shift(day, shift)
    #
    # def optimizer_helper(self, employee, day: int, shift: int, shift_len: int, sign: str):
    #     """
    #     Helper function for the optimizer. Check if the employee can work in the shift.
    #     :param employee: Employee object to be checked
    #     :param day: The day in number
    #     :param shift: The shift in number
    #     :param shift_len: The number of employees in the shift
    #     :param sign: The sign of the comparison
    #     :return: True if the employee can work in the shift, False otherwise
    #     """
    #     # Calculate the full shift amount
    #     full_shift_calc = self.MAX_EMPLOYEE_PER_SHIFT - shift_len
    #
    #     # Shabat morning need one less employee
    #     if day == 6 and shift == 0:
    #         full_shift_calc -= 1
    #
    #     # Check if the employee can work in the shift
    #     if employee in self.dict_of_shifts[day][shift] and employee.get_shift(day, shift) is False:
    #
    #         if sign == "equal":
    #             # Check if the shift is full or not
    #             if full_shift_calc == 0:
    #                 # Check if the employee can work in the shift
    #                 if self.filter_employees(employee, day, shift):
    #                     return True
    #
    #         elif sign == "greater":
    #             # The employee passed the maximum shabat shifts amount
    #             if (day == 5 and shift != 0) or (day == 6 and shift != 2):
    #                 if employee.get_shabat_counter() > self.MAX_SHABAT_SHIFTS - 1:
    #                     return False
    #
    #             # Varify that the employee dont work in this day
    #             if shift == 0:
    #                 if (employee.get_shift(day, 1) or employee.get_shift(day, 2) or
    #                         (day != 0 and employee.get_shift(day - 1, 2))):
    #                     return False
    #             elif shift == 1:
    #                 if employee.get_shift(day, 0) or employee.get_shift(day, 2):
    #                     return False
    #             elif shift == 2:
    #                 if (employee.get_shift(day, 0) or employee.get_shift(day, 1) or
    #                         (day != 6 and employee.get_shift(day + 1, 0))):
    #                     return False
    #
    #             # Verify that the shift is not full
    #             if full_shift_calc > 0:
    #                 return True
    #     return False
