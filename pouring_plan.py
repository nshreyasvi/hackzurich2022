import json
import random
import datetime
import time
import predict
from meteostat import Point

class pouring_plan:

    __no_pours = 0
    __last_updatet = 0
    __start_time = 0
    __location = 0
    __pours_dict = {}
    __strength = 0

    def __init__(self, no_pours, start_time, location, strength):
        # call data model with input
        self.__no_pours = no_pours
        self.__start_time = start_time
        self.__location = location
        self.__strength = 0

        self.__pours_dict = self.update_pours_dict()
        self.__last_updatet = time.time()
        print(self.__last_updatet)

    def from_json(self, j_str):
        j_object = json.loads(j_str)
        self.__no_pours = j_object["no_pours"]
        self.__last_updatet = j_object["last_updatet"]
        self.__start_time = j_object["start_time"]
        self.__location = j_object["location"]
        self.__pours_dict = j_object["pours_dict"]
        self.__strength = j_object["strength"]

        epoch_now = time.time()

        if self.__last_updatet < epoch_now and epoch_now > self.__start_time - 1209600:
            self.update_pours_dict()

    def update_pours_dict(self):
        time_new = self.__start_time
        for no in range(self.__no_pours):
            datestamp =  str(datetime.datetime.fromtimestamp(self.__start_time))[0:10]
            print(datestamp)
            time_fill = predict.predict_time_to_cure(self.__location, "models.csv", datestamp, self.__strength)
            time_new = time_new + time_fill

            self.__pours_dict[no] = [time_new, time_fill]

    def save_to_file(self, file_name):
        with open("/resources/" + file_name, "w") as f:
            f.write(self.serialise_self())
            f.close()

    def serialise_self(self):
        dict = {
            "no_pours": self.__no_pours,
            "last_updatet": self.__last_updatet,
            "start_time": self.__start_time,
            "location": self.__location,
            "pours_dict": self.__pours_dict,
            "strength": self.__strength
        }

        return str(json.dumps(dict))

f = pouring_plan(10,1663840800,[51.5072, -0.1276, 30],45)
print(str(f.serialise_self()))
