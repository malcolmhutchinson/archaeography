Archiving
=========

A step-by step guide to archiving and recovering the archaeological
data within the archaeography database.

A set of `pg_dump` scripts are run nightly, generating archive
files. These can be copied to another host, and run against a
PostgreSQL databse.



The easy way
------------

The easy way is to use the direct archive tables. These will make a
copy of the tables in the destination database, and involves no
mucking around.

1.  Provide a destination PostgreSQL database, preferably with a
    public schema containing no tables.

1.  Pick up the SQL archives from archive. Copy these to the
    destination host.

1.  Unpack as necessary, and run the SQL files against the destination
    database.



The hard way
------------

The hard way involves copying tables into the schema `work`. This
strips the sequences and reduces the tables to data. 

This means they can be injected into tables which have structural
changes in them, and they can be introduced to a live system (not
affecting tables in the public schema).

These can be used to bring in data to development platforms, or to
introduce arbitrary subsets of the dataset. 

It means you have to run COPY INTO scripts, to get the data from the
work schema into the destination tables.

The process is:

1.  Copy data on the source system from the public schema into the
    work schema. In shell:

        psql archaeography < ~/dev/arch/code/setup/copy-into-work.sql

2.  Export the contents of the work schema into a dump file. In shell: 

        pg_dump -n work -O archaeography | gzip > data.sql.gz

3.  Copy the resulting file to the destination system, unpack it and
    run it against the destination database. Still in shell:

        scp user@host/path/to/data.sql.gz ./
        gunzip prop_data.sql.gz
        psql archaeography < data.sql

4.  Run the script to copy these values from the work schema into public.

        $ psql -d archaeography < ~/dev/arch/code/setup/copy-into-public.sql

This method should load up a copy of the data from the source, and
take care of the id sequences too.