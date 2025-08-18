# Errors in Rulesets
* omd restart apache
* tail -f  ~/var/log/apache/error_log

# Test Manually
* cmk -v --debug -n <fritzbox_hostname>
* cmk -v --debug --dump-agent <fritzbox_hostname>
* cmk -D <fritzbox_hostname> # display datasources/hostconfig
