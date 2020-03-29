from controllers.years_controller import YearController


class PopulateYears:
    def populate(self):
        y_controller = YearController()

        # TODO: error with 2006, will debug later
        for year in range(2007, 2017):
            y_controller.post(str(year))
            print("Completed : " + str(year))


if __name__ == "__main__":
    y = PopulateYears()
    y.populate()
