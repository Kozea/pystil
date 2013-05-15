#!/bin/zsh -xe

rm -f *.zip || :
rm -f *.csv || :
rm -f *.gz || :

# Country v4 / v6
wget http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip
wget http://geolite.maxmind.com/download/geoip/database/GeoIPv6.csv.gz

# Cities v4 / v6
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/GeoLiteCity-latest.zip
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.csv.gz

# Asn v4 / v6
wget http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2.zip
wget http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2v6.zip

unzip GeoIPCountryCSV.zip
unzip GeoLiteCity-latest.zip
unzip GeoIPASNum2.zip
unzip GeoIPASNum2v6.zip

gunzip -fv GeoIPv6.csv.gz
gunzip -fv GeoLiteCityv6.csv.gz

rm -f *.zip
mv */*.csv .
rmdir * > /dev/null ||:

# create extension geoip;

sed -i 's/^\("[^"]*","[^"]*",\)"[^"]*","[^"]*",\("[^"]*","[^"]*"\)/\1\2/' GeoIPCountryWhois.csv
sed -i 1,2d GeoLiteCity-Blocks.csv
sed -i 1,2d GeoLiteCity-Location.csv

