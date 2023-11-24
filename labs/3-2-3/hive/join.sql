-- Perform the JOIN on the created tables
use hadoop;
SELECT h.country, gni, expct
FROM HDI h
JOIN EXPO e ON (h.country = e.country)
WHERE gni > 2000;
