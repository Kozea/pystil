#!/bin/zsh -xe

cd geoip
# Country v4 / v6
wget http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip
wget http://geolite.maxmind.com/download/geoip/database/GeoIPv6.csv.gz

# Cities v4 / v6
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/GeoLiteCity-latest.zip
# wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.csv.gz

# Asn v4 / v6
wget http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2.zip
wget http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2v6.zip

unzip GeoIPCountryCSV.zip
unzip GeoLiteCity-latest.zip
unzip GeoIPASNum2.zip
unzip GeoIPASNum2v6.zip

gunzip -fv GeoIPv6.csv.gz
# gunzip -fv GeoLiteCityv6.csv.gz

rm -f *.zip
mv */*.csv
rmdir * > /dev/null

# create extension geoip;

sed -i 's/^\("[^"]*","[^"]*",\)"[^"]*","[^"]*",\("[^"]*","[^"]*"\)/\1\2/' GeoIPCountryWhois.csv
sed -i 1,2d GeoLiteCity-Blocks.csv
sed -i 1,2d GeoLiteCity-Location.csv

psql -U postgres -d pystil -c "CREATE SCHEMA geoip;"
COPY geoip_country FROM '$PWD/countries.csv' WITH csv DELIMITER ',' NULL '' QUOTE '\"' ENCODING 'ISO-8859-2';

CREATE TEMPORARY TABLE geoip_city_block_tmp (
    begin_ip    BIGINT      NOT NULL,
    end_ip      BIGINT      NOT NULL,
    loc_id      INTEGER     NOT NULL
);

CREATE TEMPORARY TABLE geoip_asn_tmp (
    begin_ip    BIGINT      NOT NULL,
    end_ip      BIGINT      NOT NULL,
    name        TEXT        NOT NULL
);

COPY geoip_city_block_tmp FROM '$PWD/blocks.csv'
WITH csv DELIMITER ',' NULL '' QUOTE '\"' ENCODING 'ISO-8859-2';

COPY geoip_city_location FROM '$PWD/locations.csv'
WITH csv DELIMITER ',' NULL '' QUOTE '\"' ENCODING 'ISO-8859-2';

COPY geoip_asn_tmp FROM '$PWD/GeoIPASNum2.csv'
WITH csv DELIMITER ',' NULL '' QUOTE '\"' ENCODING 'ISO-8859-2';

INSERT INTO geoip_city_block
     SELECT geoip_bigint_to_inet(begin_ip),
            geoip_bigint_to_inet(end_ip), loc_id
       FROM geoip_city_block_tmp;

INSERT INTO geoip_asn
     SELECT geoip_bigint_to_inet(begin_ip),
            geoip_bigint_to_inet(end_ip), name
       FROM geoip_asn_tmp;

ANALYZE;"
