
python -u greenhouse.py /dev/hidraw2  | while read CO2_PPM TEMP_C; do
    NOW=$(date +%s%N)
    if [[ $CO2_PPM ]]; then
	curl  -i -s -XPOST "http://localhost:8086/write?db=greenhouse" -d @- >&2<<EOF
co2_ppm,host=clarissa,region=baker30s,room=gh1 co2_ppm=$CO2_PPM $NOW
EOF
	curl -i -s -XPOST "http://localhost:8086/write?db=greenhouse" -d @- >&2 /dev/null <<EOF
temp_c,host=clarissa,region=baker30s,room=gh1 temp_c=$TEMP_C $NOW
EOF
    fi;
    if [[ $CO2_PPM -lt 1200 ]]; then
	echo "CO2: $CO2_PPM Pumping the gas"
	mosquitto_pub -h localhost -t greenhouse/control1/cmnd/Event -m PumpGas
    fi;
    echo $CO2_PPM $TEMP_C
done

