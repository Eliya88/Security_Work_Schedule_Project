import pandas as pd


class UpdateCSV:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.df = pd.read_csv(self.csv_file_path)

    def add_new_employee(self, e_id, name, is_officer=False, shabat_night=False, has_height=True, can_drive=True,
                         shabat_count=0, nights_count=0):
        """
        This method adds a new line to the existing CSV file.
        :param e_id: The employee ID
        :param name: The employee name
        :param is_officer: Is the employee an officer
        :param shabat_night: True if the employee works in shabat night, False otherwise
        :param has_height: True if the employee has a permission to work on height, False otherwise
        :param can_drive: True if the employee has a driving approval, False otherwise
        :param shabat_count: The amount of shabat times the employee worked in a row
        :param nights_count: The amount of nights the employee worked the last two weeks
        """
        temp = {'eID': e_id, 'E_Name': name, 'Is_Officer': is_officer, 'Has_Height': has_height,
                'Can_Drive': can_drive, 'Shabat_Night': shabat_night, 'Shabat_Count': shabat_count,
                'Nights_Count': nights_count
                }
        # Add the new employee to the CSV file
        self.df = pd.concat([self.df, pd.DataFrame(temp, index=[0])], ignore_index=True)
        # Save the updated CSV file
        self.df.to_csv(self.csv_file_path, index=False)

    def update_col_value(self, e_id, col_name, value):
        """
        This method updates a specific column value in the CSV file.
        :param e_id: The employee ID
        :param col_name: The column name
        :param value: The new value
        """
        # Check if the column name exists in the CSV file and validate the value type
        if col_name in self.df.columns:
            if (col_name == 'Is_Officer' or col_name == 'Has_Height' or col_name == 'Can_Drive' or
                    col_name == 'Shabat_Night'):
                if type(value) is not bool:
                    raise ValueError(f"Expected a boolean value for {col_name} column.")
            elif col_name == 'Shabat_Count' or col_name == 'Nights_Count':
                if type(value) is not int:
                    raise ValueError(f"Expected an integer value for {col_name} column.")
            elif col_name == 'E_Name':
                if type(value) is not str:
                    raise ValueError(f"Expected a string value for {col_name} column.")

        # Update the column value
        self.df.loc[self.df['eID'] == e_id, col_name] = value
        # Save the updated CSV file
        self.df.to_csv(self.csv_file_path, index=False)

    def delete_employee_info(self, e_id):
        """
        This method deletes the employee information from the CSV file.
        """
        # Delete the employee information
        for eid in e_id:
            self.df = self.df[self.df['eID'] != eid]
        # Save the updated CSV file
        self.df.to_csv(self.csv_file_path, index=False)

    def reset_col_counter(self, col_name):
        """
        This method resets the shabat counter for all employees.
        """
        # Reset the column counter
        self.df.loc[:, col_name] = 0
        # Save the updated CSV file
        self.df.to_csv(self.csv_file_path, index=False)


csv = UpdateCSV('employee_data.csv')
csv.reset_col_counter('Nights_Count')
csv.reset_col_counter('Shabat_Count')
csv.reset_col_counter('Shabat_Night')

# # Add new employee to the department
# csv.add_new_employee(42350, 'רון פחימה', False, False, True, True, 0, 0)


# df = pd.read_csv('employee_data.csv')
# print(df.loc[df['eID'] == 42062, 'Shabat_Night'])
