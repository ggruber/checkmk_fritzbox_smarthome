#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
)

import json
import itertools

def detect_device_type(fbm):
    fbm = int(fbm)
    if fbm >> 0 & 1:
        return "HANFUNDevice"
    if fbm >> 13 & 1:
        return "HANFUNUnit"
    if fbm >> 4 & 1:
        return "AlarmSensor"
    if fbm >> 5 & 1:
        return "Button"
    if fbm >> 6 & 1:
        return "Thermostat"
    if fbm >> 9 & 1:
        return "Switch"
    if fbm >> 7 & 1:
        return "Powermeter"
    if fbm >> 10 & 1:
        return "DECTRepeater"
    if fbm >> 8 & 1:
        return "TemperatureSensor"
    if fbm >> 11 & 1:
        return "Microphone"
    if fbm >> 2 & 1 or fbm >> 17 & 1:
        return "Light"
    return "SmarthomeDevice"

def parse_fritzbox_smarthome(string_table):
    flat = list(itertools.chain.from_iterable(string_table))
    data = json.loads("".join(flat))
    return data

def discover_fritzbox_smarthome(section):
    for dev in section:
        dev_type = detect_device_type(dev.get("functionbitmask", 0))
        name = f"{dev_type} {dev['id']} {dev['name']}"
        yield Service(item=name, parameters={})


default_params = {
    "present": 1,
    "hkr": {
        "hkr_bat_always": True,
        "hkr_warn": {
            "hkr_diff_soll": 5.0,
            "hkr_bat_below": 50,
        },
        "hkr_crit": {
            "hkr_diff_soll": 10.0,
            "hkr_bat_below": 30,
        },
    },
    "humidity": {
        "humidity_warn": {
            "higher_than": 60,
            "lower_than": 40,
        },
        "humidity_crit": {
            "higher_than": 70,
            "lower_than": 30,
        },
    },
}

def check_fritzbox_smarthome(item, params, section):
    params = params or default_params

    # Device filter
    dev_id = item.split(" ")[1]
    dev = next((d for d in section if d["id"] == dev_id), None)
    if not dev:
        yield Result(state=State.CRIT, summary="Device not found")
        return

    # offline-handling
    present_param = str(params.get("present", "warn"))
    if dev.get("present") != "1":
        state = {"ok": State.OK, "warn": State.WARN, "crit": State.CRIT}.get(present_param, State.WARN)
        yield Result(state=state, summary="Device not present")
        return

    # set default-OK with Vendor/Name
    summary = f"{dev.get('manufacturer','?')} {dev.get('productname','?')} ({dev.get('name','?')})"
    yield Result(state=State.OK, summary=summary)

    data = dev.get("data", {})

    # --- thermostat (HKR aka Heizkoerperegler) ---
    if "hkr" in data:
        h = data["hkr"]

        # get warn-crit-level from ruleset
        warn_p = params["hkr"]["hkr_warn"]
        crit_p = params["hkr"]["hkr_crit"]
        warn_diff = warn_p.get("hkr_diff_soll", 5.0)
        crit_diff = crit_p.get("hkr_diff_soll", 10.0)
        warn_bat  = warn_p.get("hkr_bat_below", 50)
        crit_bat  = crit_p.get("hkr_bat_below", 30)

        # --- battery ---
        battery = int(h.get("battery", 0))
        # battery state
        if battery < crit_bat:
            yield Result(state=State.CRIT, summary=f"Battery critically low: {battery}%")
        elif battery < warn_bat:
            yield Result(state=State.WARN, summary=f"Battery low: {battery}%")

        # battery-metric (only if requested)
        if params["hkr"].get("hkr_bat_always", False):
            yield Metric("battery", battery, boundaries=(0, 100))

        # --- temperature ---
        tist = float(h.get("tist", 0)) / 2

        # temperature-metrics #1 (is-value)
        yield Metric("temp_actual", tist)

        yield Result(state=State.OK, summary=f"Temperature: {tist}°C")

        # temperature-deviation
        # target-value gives no numerical sense for computation/drawing during summer period
        # during non-heating period (summer): tsoll is reported as 253 (kindof max value?)
        #tsoll = float(h.get("tsoll", 0)) / 2 
        tsollraw = int(h.get("tsoll", 0))
        if int(h.get("summeractive"), 0) == 0 and tsollraw != 253:
            tsoll = float(tsollraw) / 2.0
            # temperature-metrics #2 (target-value)
            yield Metric("temp_target", tsoll)

            diff = abs(tsoll - tist)
            if diff > crit_diff:
                yield Result(state=State.CRIT, summary=f"Temperature deviation too high: {diff}K")
            elif diff > warn_diff:
                yield Result(state=State.WARN, summary=f"Temperature deviation: {diff}K")
        else:
            yield Result(state=State.OK, summary=f"(Sommermodus)")

        # --- windowopen ---
        wo = int(h.get("windowopenactiv", "0"))
        yield Metric("WindowOpen", wo)
        yield Result(state=State.OK, summary=f"Window is {'open' if wo==1 else 'closed'}")
            

    # --- humidity ---
    if "humidity" in data:
        rh = int(data["humidity"].get("rel_humidity", 0))
        yield Metric("humidity", rh)

        hwarn = params["humidity"]["humidity_warn"]
        hcrit = params["humidity"]["humidity_crit"]
        warn_high = hwarn.get("higher_than", 60)
        warn_low  = hwarn.get("lower_than",  40)
        crit_high = hcrit.get("higher_than", 70)
        crit_low  = hcrit.get("lower_than",  30)

        if rh > crit_high or rh < crit_low:
            yield Result(state=State.CRIT, summary=f"Humidity critical: {rh}%")
        elif rh > warn_high or rh < warn_low:
            yield Result(state=State.WARN, summary=f"Humidity warning: {rh}%")
        else:
            yield Result(state=State.OK, summary=f"Humidity OK: {rh}%")

    # --- temperatur (none-hkr devices)  ---
    # no warn/crit levels
    if "temperature" in data:
        te = float(data["temperature"].get("celsius", 0)) / 10.0
        yield Metric("temperature", te)
        yield Result(state=State.OK, summary=f"Temperature: {te}°C")

    # --- battery + batterylow (generic) ---
    if "battery" in dev and dev.get("battery") != None:
        blvl = int(dev.get("battery"))
        yield Metric("batteryLevel", blvl)
    if "batterylow" in dev and dev.get("batterylow") != None:
        bl = int(dev.get("batterylow"))
        if bl == 0:
            yield Result(state=State.OK, summary=f"Battery is ok")
        else:
            yield Result(state=State.WARN, summary=f"Battery is low")

    # --- Switch, Powermeter etc. unchanged ---
    if "switch" in data:
        st = data["switch"].get("state","0")
        mode = data["switch"].get("mode","unknown")
        yield Metric("switch_state", int(st))
        yield Result(state=State.OK, summary=f"Switch is {'ON' if st=='1' else 'OFF'} ({mode})")

    if "powermeter" in data:
        pm = data["powermeter"]
        # Power
        p = pm.get("power")
        if p is None:
            yield Result(state=State.WARN, summary="Power not available")
        else:
            power = float(p) / 1000
            yield Metric("power", power)
            yield Result(state=State.OK, summary=f"Power: {power:.2f}W")
        # Energy
        e = pm.get("energy")
        if e is None:
            yield Result(state=State.WARN, summary="Energy not available")
        else:
            energy = float(e) / 1000
            yield Metric("energy", energy)
            yield Result(state=State.OK, summary=f"Energy: {energy:.2f}kWh")
        # Voltage
        v = pm.get("voltage")
        if v is None:
            yield Result(state=State.WARN, summary="Voltage not available")
        else:
            voltage = float(v) / 1000
            yield Metric("voltage", voltage)
            yield Result(state=State.OK, summary=f"Voltage: {voltage:.1f}V")


agent_section_fritzbox_smarthome = AgentSection(
    name="fritzbox_smarthome",
    parse_function=parse_fritzbox_smarthome,
)

check_plugin_fritzbox_smarthome = CheckPlugin(
    name="fritzbox_smarthome",
    service_name="%s",
    discovery_function=discover_fritzbox_smarthome,
    check_function=check_fritzbox_smarthome,
    check_default_parameters=default_params,
    check_ruleset_name="fritzbox_smarthome",
)
