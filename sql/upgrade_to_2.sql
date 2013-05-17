begin;
alter table visit add column asn varchar;
drop table keys;
create index on visit (uuid, date);
commit;
