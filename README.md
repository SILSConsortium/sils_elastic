# sils_elastic
Resources for visualizing ILS data using Elasticsearch, Logstash, Kibana

# Installing
You can get a feel for installing the Elastic stack on a system by reading through Digital Ocean's community guides.
Beware that the Digital Ocean guides walk you through installing an older version of ELK, you can install the latest by reading the official documentation if you wish.

For CentOS 7:
https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-centos-7

For Ubuntu 16.04:
https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-ubuntu-16-04

There's also the offical documentation, which is excellent, for all three found here:
https://www.elastic.co/guide/index.html


#Getting Started / Backfilling a large historic ILS dataset into Elasticsearch
To get started you probably have a SQL query that returns interesting timestamped data, like checkouts.  Since this data can go back years and years there can be gigabytes of data returned, so it's easiest to just chunk the results of a large historic query into a set of files and then read those files into Elasticsearch using Logstash's file input plugin.  This is what is done in the example logstash config included here.

You can start with as much or as little data as you want, this is determined by how many rows are returned by your SQL query.  The file chunker just formats each row returned as JSON, and writes one row per line, 100,000 rows per file.  You could start with a SQL query that returns one month of data to get started.

The file chunker only knows how to connect to MSSQL databases, so if you aren't using Polaris, you'll need to modify it to connect to whatever type of database you're using.
The connection information is stored in environment variables in the script.

# Running logstash with the example config
The example configuration included here uses the input plugin to look for the files outpt by the file chunker, just set the path where it should look for the files.
There are two important column names returned by the SQL query that are used here, transactiondate and transactionid, the first is the timestamp of the transaction and the second is the
unique database ID.  You'll have to change these if you used different column names in your SQL query for these fields.  You'll also need to set the correct address of your Elasticsearch server.

You can run Logstash using the specified config with:

``` logstash -f logstash_config_build_from_files.conf ```
