from modules import cbpi
from modules.core.controller import FermenterController
from modules.core.props import Property
import datetime

@cbpi.fermentation_controller
class PIDFermentationChamber(FermenterController):

    @staticmethod
    def chart(fermenter):
        result = FermenterController.chart(fermenter)
        result.append({"name": "Chamber Temp", "data_type": "sensor", "data_id": fermenter.sensor2})
        result.append({"name": "Chamber Target Temp", "data_type": "chamber_target", "data_id": fermenter.id})

        return result

    p = Property.Number("Kp", True, 2)
    i = Property.Number("Ki", True, 0.0001)
    d = Property.Number("Kd", True, 2)

    def stop(self):
        super(FermenterController, self).stop()
        self.heater_off()
        self.cooler_off()

    def run(self):
        self.chamber_target_temp = self.get_target_temp()
        pid = ChamberSetpointPID(self.p, self.i, self.d)
        while self.is_running():
            temp = self.get_temp()
            target_temp = self.get_target_temp()
            chamber_temp = self.get_chamber_temp()
            self.chamber_target_temp = target_temp + int(pid.update(temp, self.get_target_temp()))

            print "Chamber Target Temp: %s", self.chamber_target_temp
            cbpi.save_to_file(self.fermenter_id, self.chamber_target_temp, prefix="chamber_target")

            if chamber_temp is None:
                self.heater_off()
            elif temp < target_temp and chamber_temp < self.chamber_target_temp:
                self.heater_on()
            elif temp >= target_temp or chamber_temp >= self.chamber_target_temp:
                self.heater_off()
            else:
                self.heater_off()

            if chamber_temp is None:
                self.cooler_off()
            elif temp > target_temp and chamber_temp > self.chamber_target_temp:
                self.cooler_on()
            elif temp <= target_temp or chamber_temp <= self.chamber_target_temp:
                self.cooler_off()
            else:
                self.cooler_off()

            self.sleep(5)

    @cbpi.try_catch(None)
    def get_chamber_temp(self):
        return self.get_sensor_value(int(self.get_fermenter().sensor2))

    @cbpi.try_catch(None)
    def cooler_on(self):
        f = self.get_fermenter()
        if f.cooler is not None:
            self.actor_on(id=int(f.cooler))

    @cbpi.try_catch(None)
    def cooler_off(self):
        f = self.get_fermenter()
        if f.cooler is not None:
            self.actor_off(int(f.cooler))

    @cbpi.try_catch(None)
    def get_fermenter(self):
        return self.api.cache.get("fermenter").get(self.fermenter_id)

class ChamberSetpointPID(object):

    def __init__(self, kp, ki, kd):
        self.k_p = float(kp)
        self.k_i = float(ki)
        self.k_d = float(kd)
        self.last_error = 0
        self.integration = 0
        self.last_output = 0

    def update(self, temp, setpoint):

        error = setpoint - temp
        if self.last_error == 0:
            self.last_error = error #catch first run error

        P_value = self.k_p * error
        D_value = -(self.k_d * (error - self.last_error))
        self.last_error = error
        if self.last_output > -15 and self.last_output < 15:
            self.integration = self.integration + error

        I_value = self.integration * self.k_i

        self.last_output = max(min(P_value + I_value + D_value, 15), -15)
        return self.last_output
