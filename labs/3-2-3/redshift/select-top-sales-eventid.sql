select top 10 myspectrum_schema.sales.eventid, 
sum(myspectrum_schema.sales.pricepaid) 
from myspectrum_schema.sales, event2
where myspectrum_schema.sales.eventid = event2.eventid
and myspectrum_schema.sales.pricepaid > 30
group by myspectrum_schema.sales.eventid
order by 2 desc;