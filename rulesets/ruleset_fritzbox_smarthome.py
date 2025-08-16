#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    Dictionary, DictElement,
    Float
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic
from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import SingleChoice, SingleChoiceElement, DefaultValue
from cmk.rulesets.v1.form_specs import BooleanChoice, DefaultValue



def _parameter_form():
    return Dictionary(
        title      = Title("Settings for Fritz!Box Smarthome Devices"),
        elements   = {
            # Offline-Devices
            'present': DictElement(
                parameter_form=SingleChoice(
                    title=Title("Offline Devices"),
                    elements=[
                        SingleChoiceElement("ok",   Title("show as OK")),
                        SingleChoiceElement("warn", Title("show as WARN")),
                        SingleChoiceElement("crit", Title("show as CRIT")),
                    ],
                    prefill=DefaultValue("warn"),
                ),
                required=True,
            ),

            # show HANFUNUnit (default: off)
            'showHFunit': DictElement(
                parameter_form=BooleanChoice(
                    title=Title("show HANFUNUnit entries"),
                    prefill=DefaultValue(False),
                ),
                required=True,
            ),

            # Thermostat-Gruppe
            'hkr': DictElement(
                parameter_form = Dictionary(
                    title    = Title("Thermostat (battery settings are also here)"),
                    elements = {
                        # Immer Batterie-Status anzeigen?
                        'hkr_bat_always': DictElement(
                            parameter_form = BooleanChoice(
                                title        = Title("Show Batterystate always"),
                                prefill= DefaultValue(True),
                            ),
                            required = True,
                        ),
                        # WARN-Thresholds
                        'hkr_warn': DictElement(
                            parameter_form = Dictionary(
                                title    = Title("Thresholds for WARN"),
                                elements = {
                                    'hkr_diff_soll': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Deviation from the target temperature (°C)"),
                                            prefill= DefaultValue(5.0),
                                        ),
                                        required = True,
                                    ),
                                    'hkr_bat_below': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Battery below (%)"),
                                            prefill= DefaultValue(50.0),
                                        ),
                                        required = True,
                                    ),
                                    'hkr_flag_error': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Errorstate"),
                                            prefill= DefaultValue(False),
                                        ),
                                        required = False,
                                    ),
                                    'hkr_flag_battery': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Batterywarning"),
                                            prefill= DefaultValue(False),
                                        ),
                                        required = False,
                                    ),
                                    'hkr_flag_window': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Window open"),
                                            prefill= DefaultValue(False),
                                        ),
                                        required = False,
                                    ),
                                }
                            ),
                            required = True,
                        ),
                        # CRIT-Thresholds
                        'hkr_crit': DictElement(
                            parameter_form = Dictionary(
                                title    = Title("Thresholds for CRIT"),
                                elements = {
                                    'hkr_diff_soll': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Deviation from the target temperature (°C)"),
                                            prefill= DefaultValue(10.0),
                                        ),
                                        required = True,
                                    ),
                                    'hkr_bat_below': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Battery below (%)"),
                                            prefill= DefaultValue(30.0),
                                        ),
                                        required = True,
                                    ),
                                    'hkr_flag_error': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Errorstate"),
                                            prefill= DefaultValue(True),
                                        ),
                                        required = False,
                                    ),
                                    'hkr_flag_battery': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Batterywarning"),
                                            prefill= DefaultValue(False),
                                        ),
                                        required = False,
                                    ),
                                    'hkr_flag_window': DictElement(
                                        parameter_form = BooleanChoice(
                                            title        = Title("On Window open"),
                                            prefill= DefaultValue(False),
                                        ),
                                        required = False,
                                    ),
                                }
                            ),
                            required = True,
                        ),
                    }
                ),
                required = True,
            ),

            # Luftfeuchtigkeit
            'humidity': DictElement(
                parameter_form = Dictionary(
                    title    = Title("Humidity"),
                    elements = {
                        'humidity_warn': DictElement(
                            parameter_form = Dictionary(
                                title    = Title("Thresholds for WARN"),
                                elements = {
                                    'higher_than': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Higher than (%)"),
                                            prefill= DefaultValue(60.0),
                                        ),
                                        required = True,
                                    ),
                                    'lower_than': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Lower than (%)"),
                                            prefill= DefaultValue(40.0),
                                        ),
                                        required = True,
                                    ),
                                }
                            ),
                            required = True,
                        ),
                        'humidity_crit': DictElement(
                            parameter_form = Dictionary(
                                title    = Title("Thresholds for CRIT"),
                                elements = {
                                    'higher_than': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Higher than (%)"),
                                            prefill= DefaultValue(70.0),
                                        ),
                                        required = True,
                                    ),
                                    'lower_than': DictElement(
                                        parameter_form = Float(
                                            title        = Title("Lower than (%)"),
                                            prefill= DefaultValue(30.0),
                                        ),
                                        required = True,
                                    ),
                                }
                            ),
                            required = True,
                        ),
                    }
                ),
                required = True,
            ),
        }
    )


# Jetzt den Ruleset-Block definieren und registrieren
rule_spec_fritzbox_smarthome = CheckParameters(
    name            = "fritzbox_smarthome",
    title           = Title("Settings for Fritz!Box Smarthome Devices"),
    topic           = Topic.GENERAL,
    parameter_form  = _parameter_form,
    condition       = HostAndItemCondition(
        item_title = Title("Device-ID")
    ),
)
