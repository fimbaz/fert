#!/bin/bash
cd /tmp/
rm -rf /var/lib/prometheus/metrics2/snapshots/
PROM_RESULT=$(curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot)
PROM_PATH=/var/lib/prometheus/metrics2/snapshots/$(jq -r .data.name <<< $PROM_RESULT)
tar cvfz /tmp/prometheus-snapshot.tar.gz $PROM_PATH
rsync -avp /tmp/prometheus-snapshot.tar.gz /mnt/s3/daily/
tar cvfz /tmp/grafana-snapshot.tar.gz /var/lib/grafana/
rsync -avp /tmp/grafana-snapshot.tar.gz /mnt/s3/daily/
