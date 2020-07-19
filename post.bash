
python -u hack.py /dev/hidraw2  | while read CO2_PPM TEMP_C; do
    NOW=$(date +%s%N)
    if [[ $CO2_PPM ]]; then
	curl -i -XPOST "http://localhost:8086/write?db=greenhouse" -d @- <<EOF
co2_ppm,host=clarissa,region=baker30s,room=gh1 co2_ppm=$CO2_PPM $NOW
EOF
	curl -i -XPOST "http://localhost:8086/write?db=greenhouse" -d @- <<EOF
temp_c,host=clarissa,region=baker30s,room=gh1 temp_c=$TEMP_C $NOW
EOF
    fi;
done

