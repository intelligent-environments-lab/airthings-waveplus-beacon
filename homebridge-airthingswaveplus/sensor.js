'use strict';
// this script is hacked together from various sources.. will need to list them all
const fs = require('fs');
let Service, Characteristic;

module.exports = (homebridge) => {
  Service = homebridge.hap.Service;
  Characteristic = homebridge.hap.Characteristic;
  homebridge.registerAccessory('homebridge-airthings-wave', 'Airthings', AirthingsPlugin);
};

class AirthingsPlugin {
  constructor(log, config) {
    this.log = log;
    this.name = config.name;
    this.name_temperature = config.name_temperature || this.name;
    this.name_humidity = config.name_humidity || this.name;
	this.name_pressure = config.name_pressure || this.name;
	this.name_radon_st = config.name_radon_st || this.name;
	this.name_radon_lt = config.name_radon_lt || this.name;
	this.name_CO2_lvl = config.name_CO2_lvl || this.name;
	this.name_VOC_lvl = config.name_VOC_lvl || this.name;
	
	
	this.carbonDioxideThreshold = Number(config["carbonDioxideThreshold"]) || 0; // ppm, 0 = OFF
	this.carbonDioxideThresholdOff = Number(config["carbonDioxideThresholdOff"]) || Number(this.carbonDioxideThreshold); // ppm, same as carbonDioxideThreshold by default, should be less than or equal to carbonDioxideThreshold
	this.vocMW = Number(config["voc_mixture_mw"]) || 72.66578273019740; // Molecular Weight (g/mol) of a reference VOC gas or mixture
	
    this.refresh = config['refresh'] || 3600; // Update every hour
    this.serialnumber = config.serialnumber;
    this.logpath = config.logpath || "/tmp/airthings.status";

    this.devicePolling.bind(this);
    this.informationService = new Service.AccessoryInformation();
    this.informationService
      .setCharacteristic(Characteristic.Manufacturer, "Airthings")
      .setCharacteristic(Characteristic.Model, "Airthings Wave")
      .setCharacteristic(Characteristic.SerialNumber, this.serialnumber)
      .setCharacteristic(Characteristic.FirmwareRevision, require('./package.json').version);

    
    this.HumiditySensorService = new Service.HumiditySensor(this.name_humidity);
    this.TemperatureSensorService = new Service.TemperatureSensor(this.name_temperature);
	this.CarbonDioxideSensorService = new Service.CarbonDioxideSensor(this.name_CO2_lvl);
	this.VOCDensitySensorService = new Service.AirQualitySensor(this.name_VOC_lvl);
	this.VOCDensitySensorService
				.setCharacteristic(Characteristic.AirQuality, "--")
				.setCharacteristic(Characteristic.VOCDensity, "--")
	this.VOCDensitySensorService
			.getCharacteristic(Characteristic.VOCDensity)
			.setProps({
				minValue: 0,
				maxValue: 100000
			});
    this.TemperatureSensorService
      .getCharacteristic(Characteristic.CurrentTemperature)
      .setProps({
        minValue: -100,
        maxValue: 100
      });

    setInterval(this.devicePolling.bind(this), this.refresh * 1000);
  }

  devicePolling() {
    var strvalues
    var valuest
    var spawn = require("child_process").spawn;
	const fs = require('fs');
	let rawdata = fs.readFileSync(this.logpath);
	let airthingsdata = JSON.parse(rawdata);
    	this.HumiditySensorService.setCharacteristic(Characteristic.CurrentRelativeHumidity, roundInt(airthingsdata.humidity));
	this.TemperatureSensorService.setCharacteristic(Characteristic.CurrentTemperature, roundInt(airthingsdata.temperature));
	  
	// Carbon Dioxide (ppm)
	var co2 = airthingsdata.CO2_lvl;
	var co2Detected;	
	var co2Before = this.CarbonDioxideSensorService.getCharacteristic(Characteristic.CarbonDioxideDetected).value;
	// this.log("CO2Before: " + co2Before);
	
	// Logic to determine if Carbon Dioxide should trip a change in Detected state
	
	this.CarbonDioxideSensorService.setCharacteristic(Characteristic.CarbonDioxideLevel, roundInt(co2));
	
	if ((this.carbonDioxideThreshold > 0) && (co2 >= this.carbonDioxideThreshold)) {
		// threshold set and CO2 HIGH
		co2Detected = 1;
		// this.log("CO2 HIGH: " + co2 + " > " + this.carbonDioxideThreshold);
	} else if ((this.carbonDioxideThreshold > 0) && (co2 < this.carbonDioxideThresholdOff)) {
		// threshold set and CO2 LOW
		co2Detected = 0;
		// this.log("CO2 NORMAL: " + co2 + " < " + this.carbonDioxideThresholdOff);
	} else if ((this.carbonDioxideThreshold > 0) && (co2 < this.carbonDioxideThreshold) && (co2 > this.carbonDioxideThresholdOff)) {
		// the inbetween...
		// this.log("CO2 INBETWEEN: " + this.carbonDioxideThreshold + " > [[[" + co2 + "]]] > " + this.carbonDioxideThresholdOff);
		co2Detected = co2Before;
	} else {
		// threshold NOT set
		co2Detected = 0;
		//// this.log("CO2: " + co2);
	}
	
	// Prevent sending a Carbon Dioxide detected update if one has not occured
	if ((co2Before == 0) && (co2Detected == 0)) {
		// CO2 low already, don't send
		//// this.log("Carbon Dioxide already low.");
	} else if ((co2Before == 0) && (co2Detected == 1)) {
		// CO2 low to high, send it!
		this.CarbonDioxideSensorService.setCharacteristic(Characteristic.CarbonDioxideDetected, co2Detected);
		//// this.log("Carbon Dioxide low to high.");
	} else if ((co2Before == 1) && (co2Detected == 1)) {
		// CO2 high to not-quite-low-enough-yet, don't send
		//// this.log("Carbon Dioxide already elevated.");
	} else if ((co2Before == 1) && (co2Detected == 0)) {
		// CO2 low to high, send it!
		//this.CarbonDioxideSensorService.setCharacteristic(Characteristic.CarbonDioxideDetected, co2Detected);
		//// this.log("Carbon Dioxide high to low.");
	} else {
		// CO2 unknown...
		//// this.log("Carbon Dioxide state unknown.");
		co2Before=co2Detected;
	}
	// end CO2
	// VOCDensity
	var voc = parseFloat(airthingsdata.VOC_lvl);
	var mw = parseFloat(this.vocMW);

	var atmos = 1;
	var atmos = parseFloat(atmos);
	var temp = parseFloat(airthingsdata.temperature);
	var vocString = "(" + voc + " * " + mw + " * " + atmos + " * 101.32) / ((273.15 + " + temp + ") * 8.3144)";
	var tvoc = (voc * mw * atmos * 101.32) / ((273.15 + temp) * 8.3144);

	  // Chemicals (ug/m^3)
	//this.VOCDensitySensorService.setCharacteristic(Characteristic.VOCDensity, tvoc);
	
	if (voc >= 0 && voc < 333) {
		voc = 1; // EXCELLENT
	} else if (voc >= 333 && voc < 1000) {
		voc = 2; // GOOD
	} else if (voc >= 1000 && voc < 3333) {
		voc = 3; // FAIR
	} else if (voc >= 3333 && voc < 8332) {
		voc = 4; // INFERIOR
	} else if (voc >= 8332) {
		voc = 5; // POOR
	} else {
		voc = 0; // Error
	}

	this.VOCDensitySensorService
		.setCharacteristic(Characteristic.VOCDensity, tvoc)
		.setCharacteristic(Characteristic.AirQuality, voc);	
	
	// TODO Pressure sensor, radon lvl.. wait for apple home compatiblity or create custom?
	
  }
  getServices() {
	return [this.informationService,  this.HumiditySensorService, this.TemperatureSensorService, this.CarbonDioxideSensorService, this.VOCDensitySensorService, ]
  }
}
function roundInt(string) {
  return Math.round(parseFloat(string) * 10) / 10;
}
