SOCK=/dev/ttyUSB2
stty -F SOCK 115200 raw
function poll_sensor() {
    echo -ne $'{"fun":"05","flag":"1"}\r'  > $SOCK
}
poll_sensor
while read -d$'}' FOO; do
    jq . <<< "${FOO}}"
    sleep 2;
    poll_sensor

done  < $SOCK
