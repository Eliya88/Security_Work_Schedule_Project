from Shift import Shift


class SecurityGuard:
    """
    This class represents a security guard in the company.
    """

    def __init__(self, name, id_number, is_officer, has_height_permission, can_drive,
                 shabat_counter=0, nights_counter=0, work_shabat_night=False):
        """ This class represents a security guard in the company. The class has the following attributes:
            :param name: The name of the guard - string
            :param id_number: The ID number of the guard - 5 digits number
            :param is_officer: True if the guard is an officer, False otherwise - boolean
            :param has_height_permission: True if the guard has a permission to work on height,
                   False otherwise - boolean
            :param can_drive: True if the guard has a driving approval, False otherwise - boolean
            :param shabat_counter: The number of shabat times the guard worked in a row.
                   after 3 shabat weeks need a break - integer
            :param nights_counter: The number of nights the guard worked in the last week.
        """
        # Validate the input parameters
        validate_guard_input(name, id_number, is_officer, has_height_permission, can_drive, shabat_counter,
                             nights_counter, work_shabat_night)
        self.__name = name
        self.__id_number = id_number
        self.__is_officer = is_officer
        self.__has_height_permission = has_height_permission
        self.__can_drive = can_drive
        self.__shabat_counter = shabat_counter
        self.__nights_counter = nights_counter
        self.__work_shabat_night = work_shabat_night
        self.__optimal_num_of_shifts = 0  # How many shifts the employee wants to work, initial from a sheets document
        self.__shifts = Shift()  # Object of the class Shift that represents the shifts of the guard in the week.

    def reset_all_shifts(self):
        """ This method resets all the shifts of the guard."""
        self.__shifts.reset_all_shifts()

    def add_shift(self, day, shift):
        """ This method adds a shift to the guard using the attribute self.shifts.
            The method also updates the counters of the guard.
        :param day: The day of the shift - integer between zero and 6 (0 - Sunday, 1 - Monday, etc.)
        :param shift: The shift of the day - integer between 0 and 2 (0 - morning, 1 - evening, 2 - night)
        """
        # Assign the shift
        self.__shifts.assign(day, shift)

        # Update the night counter
        if shift == 2:
            self.__nights_counter += 1

    def reset_nigth_counter(self):
        """ This method resets the night counter of the guard."""
        self.__nights_counter = 0

    def get_shift(self, day, shift):
        """ This method return if the guard worked in the given day and shift."""
        return self.__shifts.get_shift(day, shift)

    def set_optimal_num_of_shifts(self, num):
        """ This method set the optimal amounts of shifts the guard wants to work this week."""
        if 0 <= num <= 6:
            self.__optimal_num_of_shifts = int(num)
        elif num > 6:
            self.__optimal_num_of_shifts = 6

    def get_num_of_optimal_shifts(self):
        """ This method returns the optimal amounts of shifts the guard wants to work this week."""
        return self.__optimal_num_of_shifts

    def get_num_of_current_shifts(self):
        """ This method returns the number of shifts the guard already got."""
        return self.__shifts.get_shifts_amount()

    def get_nights_counter(self):
        """ This method returns the number of nights the guard worked the last two weeks."""
        return self.__nights_counter

    def get_shabat_counter(self):
        """ This method returns the number of shabat times the guard worked in a row."""
        return self.__shabat_counter

    def get_id_number(self):
        """ This method returns the ID number of the guard."""
        return self.__id_number

    def get_name(self):
        """ This method returns the name of the guard."""
        return self.__name

    def is_work_shabat_night(self):
        """ This method returns True if the guard work in shabat night, False otherwise."""
        return self.__work_shabat_night

    def is_allowed_to_drive(self):
        """ This method returns True if the guard has a driving approval, False otherwise."""
        return self.__can_drive

    def is_allowed_to_work_on_height(self):
        """ This method returns True if the guard has a permission to work on height, False otherwise."""
        return self.__has_height_permission

    def is_officer(self):
        """ This method returns True if the guard is an officer, False otherwise."""
        return self.__is_officer

    def count_weekly_nights(self):
        """ This method returns the number of nights the guard worked this week."""
        return self.__shifts.count_nights()

    def update_shabat_counter(self):
        """
        this method updates the amount of shabat counter if the employee works in shabat.
        if he didn't work on shabat, reset the shabat counter to zero.
        :return :shabat_counter - int
        """
        if (self.__shifts.get_shift(5, 1) or
                self.__shifts.get_shift(5, 2) or
                self.__shifts.get_shift(6, 0) or
                self.__shifts.get_shift(6, 1)):
            self.__shabat_counter += 1
        else:
            self.__shabat_counter = 0

        return self.__shabat_counter

    def delete_shift(self, day, shift):
        """ This method deletes a shift from the guard using the attribute self.shifts.
            The method also updates the counters of the guard.
        :param day: The day of the shift - integer between zero and 6 (0 - Sunday, 1 - Monday, etc.)
        :param shift: The shift of the day - integer between 0 and 2 (0 - morning, 1 - evening, 2 - night)
        """
        # Unassign the shift
        self.__shifts.unassign(day, shift)

        # Update the night counter
        if shift == 2:
            self.__nights_counter -= 1

    def __str__(self):
        """ This method returns a string representation of the guard."""
        return self.__name


def validate_guard_input(name, id_number, is_officer, has_height_permission, can_drive, shabat_counter, nights_counter,
                         work_shabat_night):
    """Validate the input parameters."""
    if not isinstance(name, str) or not name.strip():
        raise TypeError("Name must be a non-empty string.")
    if not isinstance(id_number, int) or not (10000 <= id_number <= 99999):
        raise ValueError("ID number must be a 5-digit integer.")
    if not isinstance(is_officer, bool) or not isinstance(has_height_permission, bool) or \
            not isinstance(can_drive, bool) or not isinstance(work_shabat_night, bool):
        raise TypeError("is_officer, has_height_permission, can_drive and work_shabat_night must be boolean values.")
    if not isinstance(shabat_counter, int) or not (0 <= shabat_counter <= 3):
        raise ValueError("Shabat counter must be an integer between 0 and 3.")
    if not isinstance(nights_counter, int) or not (0 <= nights_counter <= 7):
        raise ValueError("Nights counter must be an integer between 0 and 7.")
