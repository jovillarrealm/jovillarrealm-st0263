-- run these CREATEs independently
use hadoop;
CREATE TABLE word_frequencies (
  word STRING,
  count INT
);


CREATE EXTERNAL TABLE docs (line STRING) 
STORED AS TEXTFILE 
LOCATION 's3a://javillarrm-datalake/raw/datasets/gutenberg-small/';

