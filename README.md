# P1 Port Connection and Tasmota Configuration

This document describes the configuration of the Tasmota firmware for connecting a P1 Smart Meter (e.g., Sanxing SX631) and transmitting its data over MQTT. The goal is to properly prepare and transmit the data to ensure compatibility with the Domoticz plugin.

## P1 Port Connection

According to the Tasmota documentation, the connection of a P1 Smart Meter (e.g., Sanxing SX631) to the Tasmota firmware follows the [P1-Smart-Meter Tasmota Documentation](https://github.com/arendst/Tasmota/wiki/P1-Smart-Meter). This description helps with the hardware and software setup of the P1 port, processing the measurement data, and transmitting it via MQTT.

## Tasmota Script Content
[script.txt](https://github.com/csutihu/P1SmartMeter/blob/main/script.txt)

!!!This feature is not included in precompiled binaries!!! Follow this: [Smart Meter Interface](https://tasmota.github.io/docs/Smart-Meter-Interface/)

The main purpose of the Tasmota script is to process the data measured by the device and transmit it via MQTT. The key sections of the script are as follows:

### General Logic

- **D section**: Initializes the decoding string.
- **B section**: Initializes a variable (`smlj=0`) to prevent erroneous data from being sent during boot.
- **R section**: On script restart, it reinitializes the variable (`smlj=0`).
- **S section**: Checks if the device has been running for more than 22 seconds (`upsecs>22`), and only then allows the sending of MQTT teleperiod messages.

### Sensor Definitions (>M 1 section)

This part of the script defines the measured values and their corresponding MQTT keys:

#### Voltages (L1, L2, L3):

- `1-0:32.7.0` → L1 voltage (`volts_l1`)
- `1-0:52.7.0` → L2 voltage (`volts_l2`)
- `1-0:72.7.0` → L3 voltage (`volts_l3`)
- **Unit**: Volt (V)

#### Power:

- Imported power: `1-0:1.7.0` → `pwr_imp`
- Exported power: `1-0:2.7.0` → `pwr_exp`
- **Unit**: Kilowatt (kW)

#### Other Metrics:

- Power factor (`factor`): `1-0:13.7.0`
- Frequency (`freq`): `1-0:14.7.0`
- Current tariff (`tariff`): `1-0:96.14.0`

### Energy Consumption Breakdown:

#### Imported energy:

- Total: `1-0:1.8.0` → `enrg_imp`
- Tariff 1: `1-0:1.8.1` → `enrg_imp_t1`
- Tariff 2: `1-0:1.8.2` → `enrg_imp_t2`

#### Exported energy:

- Total: `1-0:2.8.0` → `enrg_exp`
- Tariff 1: `1-0:2.8.1` → `enrg_exp_t1`
- Tariff 2: `1-0:2.8.2` → `enrg_exp_t2`

**Note**: The data is structured and can be applied to various use cases (e.g., Domoticz).

## MQTT Configuration

### Important Output Data

The MQTT keys and their values published by Tasmota play a key role in the operation of the Domoticz plugin. For example:

- **Voltages**: `volts_l1`, `volts_l2`, `volts_l3`
- **Power**: `pwr_imp`, `pwr_exp`
- **Energy consumption**: `enrg_imp`, `enrg_exp`, etc.

### Teleperiod Setting

It is advisable to optimize the data sending interval (teleperiod). **Recommended value**: 60 seconds.

### Data Format

The MQTT messages arrive in a structured format, for example:

json
{
  "volts_l1": 230.1,
  "pwr_imp": 1.2,
  "enrg_imp_t1": 100.5
}

Proper formatting of the data is crucial for the Domoticz plugin to process it correctly.

## `user_config_override.h` Content

### Disabling Modules

Several unused modules are disabled in the configuration file to reduce the firmware size and increase system stability. Examples include:

- **Sensors**: BH1750, DHT, SHT3X
- **Energy monitoring**: PZEM-AC, SDM630
- **Additional integrations**: KNX, MQTT TLS

### Enabled Modules

- **USE_SCRIPT**: Required to run the Tasmota script.
- **USE_SML_M**: Supports the SML protocol.
- **USE_WEBSERVER**: Enables the Tasmota web interface.
- **USE_UFILESYS & USE_SDCARD**: File system support (e.g., for logging or script storage).

### Specific Settings

- **SML_BSIZ, TMSBSIZ**: Memory buffer size for the SML protocol to properly handle larger amounts of data coming from the P1 port. Increasing these is essential to avoid data loss.

The Tasmota firmware is modified using the **TasmoCompiler**.

## Debug and Testing

### Tasmota Logs

Checking the console or logs on the Tasmota web interface ensures that the SML data is being read and processed correctly.

### MQTT Debugging

Monitoring the MQTT messages (e.g., using MQTT Explorer) can help identify any issues. Ensure that all necessary keys (e.g., `factor`, `freq`) are properly transmitted.

## Domoticz-Specific Notes

- **MQTT Broker**: The MQTT broker address specified in the Tasmota device configuration must match the one used by the Domoticz plugin.
- **Device Identifier**: It is recommended to use a unique device name in the Tasmota configuration (e.g., `p1_smart_meter`) to help the Domoticz plugin clearly identify the data from the device.

# Domoticz Python Plugin Documentation

## Why is the Plugin Needed?

The P1 Smart Meter (e.g., Sanxing SX631) running the Tasmota firmware sends data via the MQTT protocol. This data arrives in raw form, which does not directly meet the expectations of Domoticz systems.

The purpose of the plugin is to:
1. Process the raw data published by Tasmota.
2. Convert the data into a format accepted by Domoticz.
3. Update the relevant devices in Domoticz with the processed data.

This way, the user can see the voltage, power, and energy consumption values in a clear and visual form on the Domoticz interface.

## Plugin Inputs

The plugin processes data received via the MQTT protocol. The MQTT topic for input is specified in the Tasmota device configuration.

### Key Data Points

- **Voltages**:
  - L1: `volts_l1`
  - L2: `volts_l2`
  - L3: `volts_l3`
  
- **Power**:
  - Imported power: `pwr_imp`
  - Exported power: `pwr_exp`

- **Energy Consumption**:
  - Imported energy: `enrg_imp`, `enrg_imp_t1`, `enrg_imp_t2`
  - Exported energy: `enrg_exp`, `enrg_exp_t1`, `enrg_exp_t2`

- **Other Metrics**:
  - Frequency: `freq`
  - Power factor: `factor`
  - Tariff: `tariff`

## Plugin Outputs

The plugin displays the processed data on Domoticz devices. Each measured value is shown through the appropriate type and subtype of the device:

### Key Devices

- **Voltage (L1, L2, L3)**:
  - Type: 243 (Custom Sensor)
  - Subtype: 8 (Voltage)
  
- **Power Factor**:
  - Type: 243 (Custom Sensor)
  - Subtype: 31 (% unit)
  
- **Energy Consumption**:
  - Type: 250 (Energy)
  - Subtype: Energy imported/exported by tariff.
  
- **Frequency**:
  - Type: 243 (Custom Sensor)
  - Subtype: 31 (Hz unit).

## Main Stages of Plugin Operation

1. **Initialization**:
   - Establish MQTT connection to the specified server.
   - The plugin subscribes to the MQTT_IN topic published by the Tasmota device.
   - It checks if the relevant devices exist in Domoticz and automatically creates them if not.

2. **Data Processing**:
   - Unpacks and interprets the raw data received on the MQTT_IN topic.
   - The interpreted data is assigned to the corresponding Domoticz device.

3. **Updating Data**:
   - The interpreted data is used to update the devices stored in Domoticz.
   - The device update process is executed, for example, with the following Python code:
     ```python
     self.update_device(device_id, value)
     ```

4. **Error Handling**:
   - If the MQTT connection is lost, the plugin attempts to reconnect.
   - Errors are logged to aid in troubleshooting.

## Further Development Opportunities

1. **Support for Additional Metrics**: For example, current strength, maximum power.
2. **Automatic Device Configuration**: Improve with MQTT autodiscovery or similar technology.

# Result of plugin
![image](https://github.com/user-attachments/assets/037d295d-dd4b-483a-a573-748ebb65f53f)
