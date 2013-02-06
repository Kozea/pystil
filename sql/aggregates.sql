drop schema if exists agg cascade;
create schema agg;

GRANT ALL ON SCHEMA agg TO pystil;

CREATE EXTENSION IF NOT EXISTS hstore;

CREATE FUNCTION int2interval (x integer) returns interval as $$ select $1*'1 sec'::interval $$ language sql;
CREATE CAST (integer as interval) with function int2interval (integer) as implicit;

create or replace function create_aggregate_table(table_name varchar, attributes text[], columndefs hstore, pkeys text[]) returns void as $create_aggregate_table$
	DECLARE 
		func_stmt text;
		where_clauses text[];
		group_by_clauses text[];
		attribute text;
		columndef text;
		preconds text[];
	BEGIN
		func_stmt = 'CREATE TABLE agg.' || table_name || ' as (' || $$
		  SELECT host,
		  date_trunc('day', date)::date as date,
		$$ ;
		FOREACH attribute in ARRAY attributes LOOP
		    columndef = coalesce(columndefs -> attribute, attribute);
			columndef = replace(columndef, 'NEW.', 'visit.');
			group_by_clauses = group_by_clauses || columndef;
			func_stmt = func_stmt || columndef || ' as ' || attribute || ',';
		END LOOP;
		func_stmt = func_stmt || $$ 
			count(1) as fact_count
			from visit
			where $$;
		FOREACH attribute in ARRAY pkeys LOOP
		    columndef = coalesce(columndefs -> attribute, 'NEW.' || attribute);
			preconds = preconds || (columndef || ' is not null');
			columndef = '( ' || replace(columndef, 'NEW.', 'visit.') || ' ) is not null' ;
			where_clauses = where_clauses || columndef;
		END LOOP;
		where_clauses = where_clauses || 'visit.host is not null'::text;
		preconds = preconds || 'NEW.host is not null'::text;
		func_stmt = func_stmt || array_to_string(where_clauses, ' and ');
		func_stmt = func_stmt || E' group by host, date_trunc(\'day\', date), ' || array_to_string(group_by_clauses, ', ');
		func_stmt = func_stmt || ') ;';
		EXECUTE func_stmt;
		func_stmt = 'ALTER TABLE agg.' || table_name || ' add primary key (date, host, ' || array_to_string(pkeys, ',') || ')';
		EXECUTE func_stmt;
		PERFORM agg.create_upsert_func(table_name, array_to_string(preconds, ' and ')::varchar, columndefs); 
	END;
$create_aggregate_table$ language plpgsql;


-- This function takes a tablename (existing in the agg schema, and a precondition, and creates a trigger named on the visit table
-- maintaining the aggregate table
create or replace function agg.create_upsert_func(tablename varchar, precond varchar, columndefs hstore) returns void as $create_upsert_func$
	DECLARE
		-- The function definition
		func_stmt text;
		-- A cursor for all columns in the table
		allcolumns text[];
		-- A cursor for primary key columns
		idcolumns text[];
		-- A 'buffer' for storing a columnname when iterating over one of the aboves cursor
		columnname text;
		columndef text;

		whereclauses text[];
	BEGIN	
	  	-- Fetch all columns
	    select array_agg(column_name::text) into allcolumns 
		from information_schema.columns
		where table_schema = 'agg' and table_name = tablename;

		select array_agg(column_name::text) into idcolumns
		from information_schema.columns
		where table_schema = 'agg' and table_name = tablename and column_name in 
			(SELECT kcu.column_name 
			  from information_schema.key_column_usage kcu 
			  where kcu.table_name = tablename 
			  and kcu.column_name = columns.column_name);
		
		-- Initial function declaration
		func_stmt = $func_def$ 
			create or replace function agg.upsert_$func_def$ || tablename || $func_def$ () returns TRIGGER as $func_body$
			BEGIN
			-- Set the search path to the agg schema to make it easier to reference tables.
			-- Wrap the whole logic in the supplied 'precondition'
			IF ($func_def$ || precond || $func_def$) THEN
			  UPDATE agg.$func_def$ || tablename || $func_def$ set fact_count = fact_count + 1
			  WHERE
		$func_def$;

		-- Building the update 'where' clause, iterating over idcolumns.
		FOREACH columnname in ARRAY idcolumns  LOOP
		  columndef = coalesce(columndefs -> columnname, 'NEW.' || columnname);
          IF (columnname = 'date'::text) THEN
            columndef = E'date_trunc(\'day\', NEW.date)';
          END IF;
		  whereclauses = whereclauses || ( columnname || '=' || columndef);
 		END LOOP;
		func_stmt = func_stmt || array_to_string(whereclauses, ' and ') || ';';

		-- If update matches nothing, build an insert clause
		func_stmt = func_stmt || $func_def$
			IF NOT FOUND THEN
			  INSERT INTO agg.$func_def$ || tablename || '(';
		func_stmt = func_stmt || array_to_string(allcolumns, ', ') || ') values (';
		whereclauses = array[]::text[];
		FOREACH columnname in ARRAY allcolumns LOOP
		  IF (columnname = 'fact_count') THEN
			columndef = '1';
		  ELSE 
		  	columndef = coalesce(columndefs -> columnname, 'NEW.' || columnname);
		  END IF;
		  whereclauses = whereclauses || columndef;
 		END LOOP;
		func_stmt = func_stmt || array_to_string(whereclauses, ' ,') || ' ) ;';
		func_stmt = func_stmt || $$
  			END IF;
			END IF;
			RETURN NULL;
		END $func_body$ language plpgsql;$$;
		
		-- Finally, execute the stmt
		IF (func_stmt is not null) THEN
			EXECUTE func_stmt;
		ELSE
		  RAISE EXCEPTION 'Something went bad, check the table name';
		END IF;
		EXECUTE 'drop trigger if exists agg_visit_' || tablename || ' ON public.visit;';
		EXECUTE 'create trigger agg_visit_' || tablename || $$ 
			AFTER INSERT ON VISIT FOR EACH ROW EXECUTE PROCEDURE agg.upsert_$$ || tablename || '();';

	END;
$create_upsert_func$ language plpgsql;

select create_aggregate_table('by_domain', 
  ARRAY['domain', 'subdomain'], 
  hstore('domain',  $$(case 
  				WHEN split_part(NEW.host, '.', 3) = '' 
				  then NEW.host
  				ELSE substr(NEW.host, strpos(NEW.host, '.') + 1, length(NEW.host) - strpos(NEW.host, '.') + 1) 
  			 END)$$) ||
    hstore('subdomain', $$(case 
					WHEN split_part(NEW.host, '.', 3) != ''
					  THEN split_part(NEW.host, '.', 1)
  					 ELSE NULL END)$$),
	ARRAY['domain']);

select create_aggregate_table('by_browser', 
  ARRAY['browser_name', 'browser_version', 'browser_name_version'], 
  hstore('browser_name_version', $$(
	NEW.browser_name || ' ' || split_part(NEW.browser_version, '.', 1) || (CASE 
		WHEN NEW.browser_name in ('opera', 'safari', 'chrome') 
			THEN ''
	  	ELSE '.' || split_part(NEW.browser_version, '.', 2) 
		END))$$),
	ARRAY['browser_name', 'browser_version']);


select create_aggregate_table('by_ip', ARRAY['ip'], NULL, ARRAY['ip']);

select create_aggregate_table('by_geo', ARRAY['country_code', 'country', 'city'], NULL, ARRAY['country_code', 'country', 'city']);

select create_aggregate_table('by_platform', ARRAY['platform'], NULL, ARRAY['platform']);

select create_aggregate_table('by_referrer', ARRAY['referrer', 'pretty_referrer', 'referrer_domain'], NULL, ARRAY['referrer']);

select create_aggregate_table('by_size', ARRAY['size'], NULL, ARRAY['size']);

select create_aggregate_table('by_page', ARRAY['page'], NULL, ARRAY['page']);

select create_aggregate_table('by_hash', ARRAY['page', 'hash'], NULL, ARRAY['page', 'hash']);

select create_aggregate_table('by_hour', ARRAY['hour'], 
  hstore('hour',  $$
	date_part('hour', NEW.date)$$), 
  ARRAY['hour']);

select create_aggregate_table('by_uuid', ARRAY['uuid'], NULL, ARRAY['uuid']);

grant all on agg.by_domain to pystil;
grant all on agg.by_browser to pystil;
grant all on agg.by_ip to pystil;
grant all on agg.by_geo to pystil;
grant all on agg.by_platform to pystil;
grant all on agg.by_referrer to pystil;
grant all on agg.by_size to pystil;
grant all on agg.by_page to pystil;
grant all on agg.by_hash to pystil;
grant all on agg.by_hour to pystil;
grant all on agg.by_uuid to pystil;
