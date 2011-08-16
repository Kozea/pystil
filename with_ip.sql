ALTER TABLE visit ADD COLUMN country character varying;
ALTER TABLE visit ADD COLUMN city character varying;
ALTER TABLE visit ADD COLUMN lat numeric;
ALTER TABLE visit ADD COLUMN lng numeric;


CREATE INDEX btrees ON visit USING btree (host ASC NULLS LAST, date ASC NULLS LAST);
