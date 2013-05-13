begin;
alter table visit add column asn varchar;
drop table keys;
commit;
