COPY event2 FROM 's3://jupyterjorge/raw/datasets/tickitdb/allevents_pipe.txt'
iam_role 'arn:aws:iam::170407211578:role/LabRole'
delimiter '|' timeformat 'YYYY-MM-DD HH:MI:SS' region 'us-east-1';
