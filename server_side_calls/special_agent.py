#!/usr/bin/env python3

from cmk.server_side_calls.v1 import SpecialAgentConfig, SpecialAgentCommand, noop_parser

def _agent_arguments(params, host_config):
    args = [
        "--host", host_config.ipv4_config.address,
        "--username", params.get("username", "x"),
        "--password", params.get("password").unsafe(),
        "--port", str(params.get("port", 80)),
        "--protocol", params.get("protocol", "http"),
    ]

    if params.get("ignore_ssl", False):
        args.append("--ignore-ssl")
    
    yield SpecialAgentCommand(command_arguments=args)

special_agent_fritzbox_smarthome = SpecialAgentConfig(
    name="fritzbox_smarthome",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments
)
