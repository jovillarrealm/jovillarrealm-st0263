## Información de la materia
	ST0263 Tópicos especiales en telemática
 
## Integrantes del equipo
	Jorge A. Villarreal
 	Daniel Gonzalez Bernal
  	Martin Villegas

## Profesor
	Edwin Nelson Montoya Munera, emontoya@eafit.edu.co

## Nombre del proyecto
	Proyecto 3 Tópicos Especiales en Telemática


## Arquitectura del Proyecto de Análisis de Precios de Criptomonedas en AWS 

El proyecto de análisis de precios de criptomonedas en AWS ha sido diseñado con una arquitectura robusta y escalable, aprovechando servicios clave de la plataforma en la nube de Amazon. A continuación, se detalla cada componente y su función dentro de esta arquitectura integral. 

En primer lugar, se implementa un cluster en Amazon Elastic MapReduce (EMR), configurado específicamente para ejecutar Jupyter Notebooks. EMR proporciona un entorno gestionado y escalable, ideal para el análisis de grandes conjuntos de datos. Los Jupyter Notebooks actúan como la interfaz principal para el desarrollo, ejecución y orquestación de los procesos del proyecto, facilitando la manipulación y visualización de datos de manera eficiente. 

La obtención de datos se realiza mediante la integración con la API de CoinGecko. Esta API ofrece información detallada sobre los precios de diversas criptomonedas. La selección de Jupyter Notebooks como interfaz permite la automatización del proceso de recopilación de datos, configurado para obtener actualizaciones cada minuto y medio, en línea con las limitaciones de la versión gratuita de la API. 

Posteriormente, los datos recopilados son dirigidos hacia Amazon Kinesis, un servicio de transmisión de datos en tiempo real. Kinesis facilita la ingestión y procesamiento continuo de grandes volúmenes de datos, proporcionando una solución eficaz para el análisis en tiempo real de los precios de las criptomonedas. Este flujo de datos en tiempo real permite reaccionar de manera ágil a cambios en el mercado. 

Dentro de Kinesis, se implementan procesos de análisis en tiempo real utilizando herramientas como Apache Flink o AWS Lambda. Estos procesos permiten realizar cálculos en tiempo real, transformaciones de datos y filtrado, adaptándose dinámicamente a las necesidades específicas del análisis. La flexibilidad de estas herramientas garantiza la adaptabilidad del sistema a futuras evoluciones en los requerimientos analíticos. 

Finalmente, para garantizar la persistencia de los datos procesados, se almacenan en un bucket de Amazon S3. El formato seleccionado para el almacenamiento es CSV, lo que facilita la manipulación y el análisis posterior de los datos. Amazon S3 proporciona durabilidad y escalabilidad, asegurando un acceso rápido y confiable a los datos almacenados. 

En resumen, la arquitectura del proyecto se estructura de manera que aprovecha al máximo los servicios gestionados de AWS. Desde la obtención de datos con Jupyter Notebooks y la API de CoinGecko, pasando por el análisis en tiempo real en Kinesis, hasta el almacenamiento persistente en S3, cada componente contribuye a una solución completa y eficiente para el análisis continuo de precios de criptomonedas en la nube de AWS. 


## Ejecución del proyecto


![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/712153c2-a401-4ece-a262-414ef4a76f6c)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/2671f3d5-9286-45ca-8f2a-62f5ce6229d8)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/9f702810-106d-4482-b055-4e1d6c03abac)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/fc0bca24-3b46-490c-b3a8-74ed91ad118e)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/506f7f20-d100-424f-ad66-0c18324b94a2)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/c2009c1d-b8e2-40cf-9374-cce6df1852a5)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/214439f7-5d40-4942-8235-73d776d680fb)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/5faa05eb-7957-4fd1-af05-f4e7cec991fc)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/2ad092e8-6182-446f-a2b0-9194377cdd3f)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/2b356e11-fc12-4443-9630-f0bdd8076bb2)

![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/6d7428e5-f749-4e0f-863c-b539e8af6e28)










