import re
import json
import os
import logging
from .PyViCareService import ViCareService

logger = logging.getLogger('ViCare')
logger.addHandler(logging.NullHandler())

# TODO Holiday program can still be used (parameters are there) heating.circuits." + str(self.service.circuit) + ".operating.programs.holiday
# TODO heating.dhw.schedule/setSchedule

""""Viessmann ViCare API Python tools"""

class ViCareSession:
    """This class connects to the Viesmann ViCare API.
    The authentication is done through OAuth2.
    Note that currently, a new token is generate for each run.
    """


    def __init__(self, username, password,token_file=None,circuit=0):
        """Init function. Create the necessary oAuth2 sessions
        Parameters
        ----------
        username : str
            e-mail address
        password : str
            password

        Returns
        -------
        """

        self.service = ViCareService(username, password, token_file, circuit)

    """ Set the active mode
    Parameters
    ----------
    mode : str
        Valid mode can be obtained using getModes()

    Returns
    -------
    result: json
        json representation of the answer
    """
    def setMode(self,mode):
        r=self.service.setProperty("heating.circuits." + str(self.service.circuit) + ".operating.modes.active","setMode","{\"mode\":\""+mode+"\"}")
        return r

    # Works for normal, reduced, comfort
    # active has no action
    # exetenral , standby no action
    # holiday, sheculde and unscheduled
    # activate, decativate comfort,eco
    """ Set the target temperature for the target program
    Parameters
    ----------
    program : str
        Can be normal, reduced or comfort
    temperature: int
        target temperature

    Returns
    -------
    result: json
        json representation of the answer
    """
    def setProgramTemperature(self,program: str,temperature :int):
        return self.service.setProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs."+program,"setTemperature","{\"targetTemperature\":"+str(temperature)+"}")

    def setReducedTemperature(self,temperature):
        return self.setProgramTemperature("reduced",temperature)

    def setComfortTemperature(self,temperature):
        return self.setProgramTemperature("comfort",temperature)

    def setNormalTemperature(self,temperature):
        return self.setProgramTemperature("normal",temperature)

    """ Activate a program
        NOTE
        DEVICE_COMMUNICATION_ERROR can just mean that the program is already on
    Parameters
    ----------
    program : str
        Appears to work only for comfort

    Returns
    -------
    result: json
        json representation of the answer
    """
    # optional temperature parameter could be passed (but not done)
    def activateProgram(self,program):
        return self.service.setProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs."+program,"activate","{}")

    def activateComfort(self):
        return self.activateProgram("comfort")
    """ Deactivate a program
    Parameters
    ----------
    program : str
        Appears to work only for comfort and eco (coming from normal, can be reached only by deactivating another state)

    Returns
    -------
    result: json
        json representation of the answer
    """
    def deactivateProgram(self,program):
        return self.service.setProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs."+program,"deactivate","{}")
    def deactivateComfort(self):
        return self.deactivateProgram("comfort")

    """ Set the target temperature for domestic host water
    Parameters
    ----------
    temperature : int
        Target temperature

    Returns
    -------
    result: json
        json representation of the answer
    """
    def setDomesticHotWaterTemperature(self,temperature):
        return self.service.setProperty("heating.dhw.temperature","setTargetTemperature","{\"temperature\":"+str(temperature)+"}")

    def getMonthSinceLastService(self):
        try:
            return self.service.getProperty("heating.service.timeBased")["properties"]["activeMonthSinceLastService"]["value"]
        except KeyError:
            return "error"

    def getLastServiceDate(self):
        try:
            return self.service.getProperty("heating.service.timeBased")["properties"]["lastService"]["value"]
        except KeyError:
            return "error"

    def getOutsideTemperature(self):
        try:
            return self.service.getProperty("heating.sensors.temperature.outside")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getSupplyTemperature(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".sensors.temperature.supply")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getRoomTemperature(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".sensors.temperature.room")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getModes(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.modes.active")["actions"][0]["fields"][0]["enum"]
        except KeyError:
            return "error"

    def getActiveMode(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.modes.active")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getHeatingCurveShift(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".heating.curve")["properties"]["shift"]["value"]
        except KeyError:
            return "error"

    def getHeatingCurveSlope(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".heating.curve")["properties"]["slope"]["value"]
        except KeyError:
            return "error"

    def getBoilerTemperature(self):
        try:
            return self.service.getProperty("heating.boiler.sensors.temperature.main")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getActiveProgram(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs.active")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getPrograms(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs")["entities"][9]["properties"]["components"]
        except KeyError:
            return "error"

    def getDesiredTemperatureForProgram(self , program):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs."+program)["properties"]["temperature"]["value"]
        except KeyError:
            return "error"

    def getCurrentDesiredTemperature(self):
        try:
            return self.service.getProperty("heating.circuits." + str(self.service.circuit) + ".operating.programs."+self.getActiveProgram())["properties"]["temperature"]["value"]
        except KeyError:
            return "error"

    def getDomesticHotWaterConfiguredTemperature(self):
        try:
            return self.service.getProperty("heating.dhw.temperature")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getDomesticHotWaterStorageTemperature(self):
        try:
            return self.service.getProperty("heating.dhw.sensors.temperature.hotWaterStorage")["properties"]["value"]["value"]
        except KeyError:
            return "error"

    def getDomesticHotWaterMaxTemperature(self):
        try:
            return self.service.getProperty("heating.dhw.temperature")["actions"][0]["fields"][0]["max"]
        except KeyError:
            return "error"

    def getDomesticHotWaterMinTemperature(self):
        try:
            return self.service.getProperty("heating.dhw.temperature")["actions"][0]["fields"][0]["min"]
        except KeyError:
            return "error"

    def getGasConsumptionHeatingDays(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['day']['value']
        except KeyError:
            return "error"

    def getGasConsumptionHeatingToday(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['day']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionHeatingWeeks(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['week']['value']
        except KeyError:
            return "error"

    def getGasConsumptionHeatingThisWeek(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['week']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionHeatingMonths(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['month']['value']
        except KeyError:
            return "error"

    def getGasConsumptionHeatingThisMonth(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['month']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionHeatingYears(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['year']['value']
        except KeyError:
            return "error"

    def getGasConsumptionHeatingThisYear(self):
        try:
            return self.service.getProperty('heating.gas.consumption.heating')['properties']['year']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterDays(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['day']['value']
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterToday(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['day']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterWeeks(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['week']['value']
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterThisWeek(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['week']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterMonths(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['month']['value']
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterThisMonth(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['month']['value'][0]
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterYears(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['year']['value']
        except KeyError:
            return "error"

    def getGasConsumptionDomesticHotWaterThisYear(self):
        try:
            return self.service.getProperty('heating.gas.consumption.dhw')['properties']['year']['value'][0]
        except KeyError:
            return "error"

    def getCurrentPower(self):
        try:
            return self.service.getProperty('heating.burner.current.power')['properties']['value']['value']
        except KeyError:
            return "error"

    def getBurnerActive(self):
        try:
            return self.service.getProperty("heating.burner")["properties"]["active"]["value"]
        except KeyError:
            return "error"
