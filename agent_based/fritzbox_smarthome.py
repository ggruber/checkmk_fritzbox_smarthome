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
    "hkr": {
        "bat_warn": 30,
        "bat_crit": 20,
        "diff_warn": 5.0,
        "diff_crit": 8.0,
    },
    "humidity": {
        "warn": (60, 40),
        "crit": (70, 30),
    },
}

def check_fritzbox_smarthome(item, params, section):
    params = params or default_params
    dev = next((d for d in section if d["id"] == item.split(" ")[1]), None)

    if not dev:
        yield Result(state=State.CRIT, summary="Device not found")
        return

    if dev.get("present") != "1":
        yield Result(state=State.WARN, summary="Device not present")
        return

    summary = f"{dev['manufacturer']} {dev['productname']} ({dev['name']})"
    yield Result(state=State.OK, summary=summary)

    data = dev.get("data", {})

    if "hkr" in data:
        hkr = data["hkr"]
        tist = float(hkr.get("tist", 0)) / 2
        tsoll = float(hkr.get("tsoll", 0)) / 2
        diff = abs(tsoll - tist)
        battery = int(hkr.get("battery", 0))

        yield Metric("temp_actual", tist)
        yield Metric("temp_target", tsoll)
        yield Metric("battery", battery, boundaries=(0, 100))

        if battery < params["hkr"]["bat_crit"]:
            yield Result(state=State.CRIT, summary=f"Battery critically low: {battery}%")
        elif battery < params["hkr"]["bat_warn"]:
            yield Result(state=State.WARN, summary=f"Battery low: {battery}%")

        if diff > params["hkr"]["diff_crit"]:
            yield Result(state=State.CRIT, summary=f"Temperature deviation too high: {diff}°C")
        elif diff > params["hkr"]["diff_warn"]:
            yield Result(state=State.WARN, summary=f"Temperature deviation: {diff}°C")

    if "humidity" in data:
        rh = int(data["humidity"].get("rel_humidity", 0))
        yield Metric("humidity", rh)
        if rh > params["humidity"]["crit"][0] or rh < params["humidity"]["crit"][1]:
            yield Result(state=State.CRIT, summary=f"Humidity critical: {rh}%")
        elif rh > params["humidity"]["warn"][0] or rh < params["humidity"]["warn"][1]:
            yield Result(state=State.WARN, summary=f"Humidity warning: {rh}%")
        else:
            yield Result(state=State.OK, summary=f"Humidity OK: {rh}%")

    if "switch" in data:
        switch_state = data["switch"].get("state", "0")
        mode = data["switch"].get("mode", "unknown")
        yield Metric("switch_state", int(switch_state))
        yield Result(state=State.OK, summary=f"Switch is {'ON' if switch_state == '1' else 'OFF'} ({mode})")

    if "powermeter" in data:
        pm = data["powermeter"]
        
        if pm.get("power", 0) == None:
            yield Result(state=State.WARN, summary="Power not available")
        else:
            power = float(pm.get("power", 0)) / 1000
            yield Metric("power", power)
            yield Result(state=State.OK, summary=f"Power: {power:.2f}W")
        
        if pm.get("energy", 0) == None:
            yield Result(state=State.WARN, summary="Energy not available")
        else:
            energy = float(pm.get("energy", 0)) / 1000
            yield Metric("energy", energy)
            yield Result(state=State.OK, summary=f"Energy: {energy:.2f}kWh")


        if pm.get("voltage", 0) == None:    
            yield Result(state=State.WARN, summary="Voltage not available")
        else:
            voltage = float(pm.get("voltage", 0)) / 1000
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
