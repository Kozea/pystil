#!/bin/sh -xe
# Getting only if the file is new
wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
# Archiving archive to avoid redownload
cp GeoLiteCity.dat.gz ip.db.gz
# Install the db file
gunzip -fv ip.db.gz
