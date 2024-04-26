import pandas as pd


class Shift:
    """
    Represents a single work shift for a security guard.
    """

    def __init__(self):
        """
        Initializes a Shift object.
        """
        self.__shifts_df = pd.DataFrame({'day': [], 'shift': [], 'is_assigned': []})

        # initial shifts to False
        for day in range(7):
            for shift in range(3):
                temp = pd.DataFrame({'day': day, 'shift': shift, 'is_assigned': False}, index=[0])
                self.__shifts_df = pd.concat([self.__shifts_df, temp], ignore_index=True)

    def assign(self, day, shift):
        """
        Marks the shift as assigned.
        """
        if not (0 <= day <= 6):
            raise ValueError("Invalid day. Day must be an integer between 0 and 6.")

        if not (0 <= shift <= 2):
            raise ValueError("Invalid shift type. Shift type must be 'morning', 'evening', or 'night'.")

        self.__shifts_df.loc[
            (self.__shifts_df['day'] == day) & (self.__shifts_df['shift'] == shift), 'is_assigned'] = True

    def unassign(self, day, shift):
        """
        Marks the shift as unassigned.
        """
        if not (0 <= day <= 6):
            raise ValueError("Invalid day. Day must be an integer between 0 and 6.")

        if not (0 <= shift <= 2):
            raise ValueError("Invalid shift type. Shift type must be 'morning', 'evening', or 'night'.")

        self.__shifts_df.loc[
            (self.__shifts_df['day'] == day) & (self.__shifts_df['shift'] == shift), 'is_assigned'] = False

    def get_shift(self, day, shift):
        """
        Returns a formatted string representing the details of the shift, including assignment status
        """
        if not (0 <= day <= 6):
            raise ValueError("Invalid day. Day must be an integer between 0 and 6.")

        if not (0 <= shift <= 2):
            raise ValueError("Invalid shift type. Shift type must be 'morning', 'evening', or 'night'.")

        return self.__shifts_df[
            (self.__shifts_df['day'] == day) & (self.__shifts_df['shift'] == shift)]['is_assigned'].values[0]

    def get_shifts_amount(self):
        """
        Returns the number of shifts in the shifts DataFrame.
        """
        return self.__shifts_df['is_assigned'].sum()

    def count_nights(self):
        """
        Returns the number of night shifts in the shifts DataFrame.
        """
        return self.__shifts_df[self.__shifts_df['shift'] == 2]['is_assigned'].sum()

    def reset_all_shifts(self):
        """
        Reset all shifts to False.
        """
        self.__shifts_df['is_assigned'] = False
