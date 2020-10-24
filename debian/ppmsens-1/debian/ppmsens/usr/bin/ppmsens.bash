SOCK=${1:-/dev/ttyUSB0}

stty -F $SOCK 115200 raw
function poll_sensor() {
    echo -ne $'{"fun":"05","flag":"1"}\r'  > $SOCK
}

while true; do
    poll_sensor
      while read -t2 -d$'}' FOO; do
	  sleep 2;
	  echo "$FOO}"
      done  < $SOCK | jq 'select(.res == "4") | del(.d,.m,.y,.h,.min,.sec)' |  tr -d '":{},' | tr -s ' ' |  cut -d ' ' -f2,3 | tr -s '\n' | \
	  while read -a REC; do
	      COL=${REC[0]}
	      COL=${COL//\./_}
	      echo $COL
	      if [[ $COL ]]; then
		 curl -X POST -d @- "http://localhost:8086/write?db=greenhouse" <<EOF 
$COL,host=clarissa,region=baker30s,room=upstairs $COL=${REC[1]} $(date '+%s')000000000
EOF
	      fi
	  done
done
