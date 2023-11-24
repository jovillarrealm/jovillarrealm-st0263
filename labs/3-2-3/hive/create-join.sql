-- run these CREATEs independently

-- Create the `hdi` table
use hadoop;
CREATE EXTERNAL TABLE HDI (id INT, country STRING, hdi FLOAT, lifeex INT, mysch INT, eysch INT, gni INT) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
LOCATION 's3a://javillarrm-datalake/raw/datasets/onu/hdi'

-- Create the `EXPO` table
use hadoop;
CREATE EXTERNAL TABLE EXPO (
  country STRING,
  expct FLOAT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3a://javillarrm-datalake/raw/datasets/onu/export';

