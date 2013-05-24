BEGIN;
    ALTER TABLE visit RENAME to visit_;
    CREATE TABLE visit (like visit_ including defaults including indexes);
    ALTER TABLE visit OWNER to pystil;
COMMIT;


BEGIN;
    ALTER TABLE visit_ DISABLE TRIGGER ALL;
    ALTER TABLE visit_ 
        ADD column day date,
        ADD column hour integer,
        ADD column subdomain varchar,
        ADD column domain varchar,
        ADD column browser_name_version varchar;
    UPDATE visit_ set day = date_trunc('day', date),
                     hour = date_part('hour', date),
                     subdomain = CASE WHEN split_part(host, '.', 3) != '' THEN split_part(host, '.', 1) ELSE NULL END,
                    domain = CASE WHEN split_part(host, '.', 3) = '' THEN host ELSE substr(host, strpos(host, '.') + 1, length(host) - strpos(host, '.') + 1) END,
                    browser_name_version = browser_name || ' ' || split_part(browser_version, '.', 1) || (
                        CASE WHEN browser_name IN ('opera', 'safari', 'chrome') THEN '' 
                        ELSE split_part(browser_version, '.', 2) END);
COMMIT;

BEGIN;
    ALTER table visit RENAME to temp_visit;
    DROP schema agg CASCADE;
    ALTER TABLE temp_visit 
        ADD column day date,
        ADD column hour integer,
        ADD column subdomain varchar,
        ADD column domain varchar,
        ADD column browser_name_version varchar;
    UPDATE temp_visit set day = date_trunc('day', date),
                     hour = date_part('hour', date),
                     subdomain = CASE WHEN split_part(host, '.', 3) != '' THEN split_part(host, '.', 1) ELSE NULL END,
                    domain = CASE WHEN split_part(host, '.', 3) = '' THEN host ELSE substr(host, strpos(host, '.') + 1, length(host) - strpos(host, '.') + 1) END,
                    browser_name_version = browser_name || ' ' || split_part(browser_version, '.', 1) || (
                        CASE WHEN browser_name IN ('opera', 'safari', 'chrome') THEN '' 
                        ELSE split_part(browser_version, '.', 2) END);


    ALTER TABLE visit_ RENAME to visit;
    
    CREATE SCHEMA partman;
    CREATE EXTENSION pg_partman SCHEMA partman;
    ALTER table visit alter date set not null;
    -- Dynamic allows for more than one table to be populated, static needs
    -- "run maintenance"
    SELECT partman.create_parent('public.visit', 'date', 'time-dynamic', 'monthly', 4);
    -- Populates the partition, one at a time. 24 = 24 iterations, 24
    -- partitions, two years worth of visits.
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    select partman.partition_data_time('public.visit', 3);
COMMIT;

BEGIN;
    INSERT INTO visit (select * from temp_visit);
COMMIT;
