
"""
<plugin key="TasmotaP1" name="Tasmota P1 Energy Handler" author="csuti" version="1.2.0" externallink="http://yourwebsite.com">
    <params>
        <param field="Address" label="MQTT Server Address" width="300px" required="true" default="localhost"/>
        <param field="Port" label="MQTT Server Port" width="100px" required="true"  default="1883"/>
        <param field="Mode1" label="MQTT In Topic" width="300px" required="true" default="tele/p1meter/SENSOR"/>
    </params>
</plugin>
"""

import Domoticz
import json
import paho.mqtt.client as mqtt

class P1EnergyMeterPlugin:
    def __init__(self):
        self.mqtt_client = None
        self.server = None
        self.mqtt_port = None
        self.mqtt_in_topic = None

    def onStart(self):
        Domoticz.Log("Plugin is starting.")

        self.server = Parameters["Address"]
        self.mqtt_port = int(Parameters["Port"])
        self.mqtt_in_topic = Parameters["Mode1"]
        Domoticz.Log(f"MQTT Server Address: {self.server}")

        if not self.server or not isinstance(self.server, str) or self.server.strip() == "":
            Domoticz.Error("MQTT Server Address is invalid or not set.")
            return

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.onMQTTConnect
        self.mqtt_client.on_message = self.onMQTTMessage
        self.mqtt_client.connect(self.server, self.mqtt_port, 60)
        self.mqtt_client.loop_start()

        Domoticz.Log(f"MQTT client connected and subscribed to topic: {self.mqtt_in_topic}")
        self.mqtt_client.subscribe(self.mqtt_in_topic)

        self.initialize_devices()

    def onStop(self):
        Domoticz.Log("Plugin is stopping.")
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

    def onMQTTConnect(self, client, userdata, flags, rc):
        Domoticz.Log(f"Connected to MQTT broker with code {rc}.")
        client.subscribe(self.mqtt_in_topic)

    def onMQTTMessage(self, client, userdata, msg):
        payload = msg.payload.decode()
        Domoticz.Log(f"Received MQTT message on topic: {msg.topic}, message: {payload}")

        if msg.topic == self.mqtt_in_topic:
            self.process_mqtt_message(payload)

    def process_mqtt_message(self, payload):
        try:
            data = json.loads(payload)

            mvm_data = data.get("MVM", {})
            volts_l1 = mvm_data.get("volts_l1", 0)
            volts_l2 = mvm_data.get("volts_l2", 0)
            volts_l3 = mvm_data.get("volts_l3", 0)
            freq = mvm_data.get("freq", 0)
            factor = mvm_data.get("factor", 0)
            tariff = mvm_data.get("tariff", 0)
            usage1 = int(mvm_data.get("enrg_imp_t1", 0) * 1000)
            usage2 = int(mvm_data.get("enrg_imp_t2", 0) * 1000)
            return1 = int(mvm_data.get("enrg_exp_t1", 0) * 1000)
            return2 = int(mvm_data.get("enrg_exp_t2", 0) * 1000)
            cons = int(mvm_data.get("pwr_imp", 0) * 1000)
            prod = int(mvm_data.get("pwr_exp", 0) * 1000)

            # Update devices
            self.update_device(1, volts_l1)
            self.update_device(2, volts_l2)
            self.update_device(3, volts_l3)
            self.update_device(4, freq, axisUnit="Hz")
            self.update_device(5, factor, axisUnit="%")
            self.update_device(6, f"{usage1};{usage2};{return1};{return2};{cons};{prod}")
            self.update_device(7, tariff)

        except Exception as e:
            Domoticz.Error(f"Error processing MQTT message: {e}")

    def initialize_devices(self):	
        devices_config = [
            (1, "L1 Voltage", 243, 8),
            (2, "L2 Voltage", 243, 8),
            (3, "L3 Voltage", 243, 8),
            (4, "Electric Frequency", 243, 31, "1;Hz"),
            (5, "Power Factor", 243, 31, "1;%"),
            (6, "Electric Energy", 250, 1),
            (7, "Electric Tariff", 243, 31),
        ]

        for unit, name, dtype, stype, *options in devices_config:
            if unit not in Devices:
                Domoticz.Device(
                    Unit=unit,
                    Name=name,
                    Type=dtype,
                    Subtype=stype,
                    Options={"Custom": options[0]} if options else {}
                ).Create()
                Domoticz.Log(f"Device created: {name} (Unit: {unit})")

    def update_device(self, unit, value, axisUnit=None):
        if unit in Devices:
            device = Devices[unit]
            device.Update(nValue=0, sValue=str(value))
            Domoticz.Log(f"Device updated: {device.Name} (Unit: {unit}) with value: {value}")
        else:
            Domoticz.Error(f"Device with Unit {unit} does not exist. Cannot update.")

# Plugin instantiation
global _plugin
_plugin = P1EnergyMeterPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onMessage(Connection, Data):
    pass

def onCommand(Unit, Command, Level, Hue):
    pass

def onHeartbeat():
    pass
