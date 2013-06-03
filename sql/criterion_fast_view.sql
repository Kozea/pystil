create or replace function create_criterion_view() returns void as $create_criterion_view$
declare
    first boolean;
    stmt text;
    s text;
begin
    stmt = 'create or replace view criterion_view as (';
    first = true;
    for s in select '(select * from ' || c.relname || ' order by date desc)'
        from pg_inherits
             join pg_class as c on (inhrelid=c.oid)
             join pg_class as p on (inhparent=p.oid)
        where p.relname = 'visit'
        order by c.relname desc
    loop
        if first then
            stmt = stmt || s;
            first = false;
        else
            stmt = stmt || ' union all ' || s;
        end if;
    end loop;
    stmt = stmt || ');';
    execute stmt;
end;
$create_criterion_view$ language plpgsql;

select create_criterion_view();
