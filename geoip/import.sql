\connect pystil pystil
drop schema if exists geoip cascade;
create schema geoip;
\connect pystil postgres
create extension if not exists ip4r;
\connect pystil pystil

CREATE TABLE geoip.country (
    ipr iprange NOT NULL,
    country_code CHAR(2) NOT NULL,
    country_name VARCHAR NOT NULL
);
CREATE INDEX ipranges_ipr_country_idx ON geoip.country USING gist (ipr);

CREATE TABLE geoip.city (
    ipr iprange NOT NULL,
    country_code CHAR(2) NOT NULL,
    region VARCHAR,
    city VARCHAR,
    postal_code VARCHAR,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    metro_code INTEGER,
    area_code INTEGER
);
CREATE INDEX ipranges_ipr_city_idx ON geoip.city USING gist (ipr);

CREATE TABLE geoip.asn (
    ipr iprange NOT NULL,
    asn VARCHAR NOT NULL
);
CREATE INDEX ipranges_ipr_asn_idx ON geoip.asn USING gist (ipr);


CREATE OR REPLACE FUNCTION geoip_bigint_to_str(p_ip BIGINT) RETURNS text AS $$
    SELECT (($1 >> 24 & 255) || '.' || ($1 >> 16 & 255) || '.' || ($1 >> 8 & 255) || '.' || ($1 & 255))
$$ LANGUAGE sql strict immutable;

CREATE TEMPORARY TABLE geoip_country_tmp (
    begin_str_ip    VARCHAR      NOT NULL,
    end_str_ip      VARCHAR      NOT NULL,
    country     VARCHAR         NOT NULL,
    name        VARCHAR    NOT NULL
);

\copy geoip_country_tmp from 'GeoIPCountryWhois.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

CREATE TEMPORARY TABLE geoip_country_v6_tmp (
    begin_str_ip    VARCHAR      NOT NULL,
    end_str_ip      VARCHAR      NOT NULL,
    begin_ip    VARCHAR      NOT NULL,
    end_ip      VARCHAR      NOT NULL,
    country     VARCHAR         NOT NULL,
    name        VARCHAR    NOT NULL
);

\copy geoip_country_v6_tmp from 'GeoIPv6.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

insert into geoip.country
       select (trim(begin_str_ip) || '-' || trim(end_str_ip))::iprange,
              trim(country), trim(name)
       from geoip_country_tmp;

insert into geoip.country
       select (trim(begin_str_ip) || '-' || trim(end_str_ip))::iprange,
              trim(country), trim(name)
       from geoip_country_v6_tmp;

CREATE TEMPORARY TABLE geoip_city_location_tmp (
    loc_id      INTEGER         PRIMARY KEY,
    country     VARCHAR         NOT NULL,
    region      VARCHAR,
    city        VARCHAR,
    postal_code VARCHAR,
    latitude    DOUBLE PRECISION,
    longitude   DOUBLE PRECISION,
    metro_code  INTEGER,
    area_code   INTEGER
);

\copy geoip_city_location_tmp from 'GeoLiteCity-Location.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';


CREATE TEMPORARY TABLE geoip_city_block_tmp (
    begin_ip    BIGINT            NOT NULL,
    end_ip      BIGINT            NOT NULL,
    loc_id      INTEGER         NOT NULL    REFERENCES geoip_city_location_tmp(loc_id)
);

\copy geoip_city_block_tmp from 'GeoLiteCity-Blocks.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

insert into geoip.city
       select (geoip_bigint_to_str(begin_ip) || '-' || geoip_bigint_to_str(end_ip))::iprange,
              trim(country), trim(region), trim(city), trim(postal_code), latitude, longitude, metro_code, area_code
       from geoip_city_block_tmp natural join geoip_city_location_tmp;


CREATE TEMPORARY TABLE geoip_city_location_v6_tmp (
    begin_str_ip     VARCHAR         NOT NULL,
    end_str_ip      VARCHAR         NOT NULL,
    begin_ip    VARCHAR      NOT NULL,
    end_ip      VARCHAR      NOT NULL,
    country     VARCHAR        ,
    region      VARCHAR,
    city        VARCHAR,
    latitude    DOUBLE PRECISION,
    longitude   DOUBLE PRECISION,
    postal_code VARCHAR,
    metro_code  INTEGER,
    area_code   INTEGER
);

\copy geoip_city_location_v6_tmp from 'GeoLiteCityv6.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

insert into geoip.city
       select (trim(begin_str_ip) || '-' || trim(end_str_ip))::iprange,
              trim(country), trim(region), trim(city), trim(postal_code), latitude, longitude, metro_code, area_code
       from geoip_city_location_v6_tmp;

CREATE TEMPORARY TABLE geoip_asn_tmp (
    begin_ip    BIGINT      NOT NULL,
    end_ip      BIGINT      NOT NULL,
    name        VARCHAR        NOT NULL
);

\copy geoip_asn_tmp from 'GeoIPASNum2.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

insert into geoip.asn
       select (geoip_bigint_to_str(begin_ip) || '-' || geoip_bigint_to_str(end_ip))::iprange,
              trim(name)
       from geoip_asn_tmp;

CREATE TEMPORARY TABLE geoip_asn_v6_tmp (
    begin_str_ip     VARCHAR         NOT NULL,
    end_str_ip      VARCHAR         NOT NULL,
    begin_ip    VARCHAR      NOT NULL,
    end_ip      VARCHAR      NOT NULL,
    name        VARCHAR        NOT NULL
);

\copy geoip_asn_v6_tmp from 'GeoIPASNumv6-2.csv' with csv delimiter ',' null '' quote '"' encoding 'ISO-8859-2';

insert into geoip.asn
       select (trim(begin_str_ip) || '-' || trim(end_str_ip))::iprange,
              trim(name)
       from geoip_asn_v6_tmp;

VACUUM;
ANALYZE;
