create external schema myspectrum_schema
from data catalog
database 'myspectrum_db'
iam_role 'arn:aws:iam::170407211578:role/LabRole'
create external database if not exists;