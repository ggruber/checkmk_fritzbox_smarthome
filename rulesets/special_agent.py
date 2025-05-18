from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    String,
    Password,
    Integer,
    SingleChoice,
    SingleChoiceElement,
    BooleanChoice,
    DefaultValue,
    migrate_to_password
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Help, Title


def _formspec():
    return Dictionary(
        title=Title("Fritz!Box Smarthome Devices"),
        help_text=Help("Configure access to the Fritz!Box smarthome data."),
        elements={
            "username": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("Username for login."),
                    prefill=DefaultValue("smarthome"),
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Password"),
                    help_text=Help("Password for the user."),
                    migrate=migrate_to_password,
                ),
            ),
            "port": DictElement(
                required=True,
                parameter_form=Integer(
                    title=Title("Port"),
                    help_text=Help("Port number of the Fritz!Box."),
                    prefill=80,
                ),
            ),
            "protocol": DictElement(
                required=True,
                parameter_form=SingleChoice(
                    title=Title("Protocol"),
                    help_text=Help("Select whether to use HTTP or HTTPS."),
                    elements=[
                        SingleChoiceElement("http", Title("HTTP")),
                        SingleChoiceElement("https", Title("HTTPS")),
                    ],
                    prefill=DefaultValue("http"),
                ),
            ),
            "ignore_ssl": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    title=Title("Ignore SSL certificate"),
                    help_text=Help("Disable SSL certificate verification."),
                    prefill=DefaultValue(False),
                ),
            ),
        },
    )

rule_spec_fritzbox_smarthome = SpecialAgent(
    topic=Topic.NETWORKING,
    name="fritzbox_smarthome",
    title=Title("Fritz!Box Smarthome Devices"),
    parameter_form=_formspec,
)
