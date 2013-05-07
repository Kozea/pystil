#!/bin/zsh -xe
# Getting only if the file is new
wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
# Archiving archive to avoid redownload
cp GeoLiteCity.dat.gz ip.db.gz
# Install the db file
gunzip -fv ip.db.gz


#
cd geoip
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
mv */*.csv
rmdir * > /dev/null

# create extension geoip;

sed 's/^\("[^"]*","[^"]*",\)"[^"]*","[^"]*",\("[^"]*","[^"]*"\)/\1\2/' GeoIPCountryWhois.csv > countries.csv
tail -$((`wc -l GeoLiteCity-Blocks.csv | awk '{print $1}'`-2)) GeoLiteCity-Blocks.csv > blocks.csv
tail -$((`wc -l GeoLiteCity-Location.csv | awk '{print $1}'`-2)) GeoLiteCity-Location.csv > locations.csv

psql -U postgres -d pystil -c "
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
