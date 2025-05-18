# Fehler in Rulesets
* omd restart apache
* tail -f  ~/var/log/apache/error_log

# Manuell testen
* cmk -v --debug -n fritzbox
* cmk -v --debug --dump-agent  fritzbox
* cmk -D fritzbox # anzeigen der datasources /hostconfig