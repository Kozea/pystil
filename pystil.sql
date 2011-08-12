CREATE ROLE pystil LOGIN ENCRYPTED PASSWORD 'md55aca61e57e322fd4708dda71f56eab22' VALID UNTIL 'infinity';
CREATE DATABASE pystil WITH ENCODING='UTF8' OWNER=pystil TEMPLATE=template0 CONNECTION LIMIT=-1;

-- Table: visit

-- DROP TABLE visit;

CREATE TABLE visit
(
  browser_name character varying,
  browser_version character varying,
  date timestamp without time zone,
  hash character varying,
  host character varying,
  ip character varying,
  "language" character varying,
  last_visit timestamp without time zone,
  page character varying,
  platform character varying,
  query character varying,
  referrer character varying,
  site character varying,
  size character varying,
  "time" integer,
  uuid character varying NOT NULL,
  client_tz_offset integer,
  CONSTRAINT visit_pkey PRIMARY KEY (uuid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE visit OWNER TO pystil;

