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

Para la arquitectura de este proyecto se implementó un clúster EMR en AWS, entre las apps instaladas por defecto dejamos configurado Jupyter Notebooks. Los Jupyter Notebooks fueron usados como la interfaz principal para el desarrollo y ejecución de los procesos del proyecto. La obtención de datos vivos se realizó mediante la integración con la API de CoinGecko. Esta API ofrece información detallada sobre los precios de diversas criptomonedas. Debido a las limitaciones de la versión gratuita de la API, la actualización de datos se realiza solamente cada minuto y medio, pero para efectos académicos consideramos que el sistema igualmente es válido.
Los datos recopilados con la API de CoinGecko son entonces dirigidos hacia Amazon Kinesis, un servicio de transmisión de datos en tiempo real. Kinesis facilita la ingestión y procesamiento continuo de grandes volúmenes de datos, proporcionando una solución eficaz para el análisis en tiempo real de los precios de las criptomonedas. Este flujo de datos en tiempo real permite reaccionar de manera ágil a cambios en el mercado.
 
Finalmente, para garantizar la persistencia de los datos procesados, se almacenan en un bucket de Amazon S3. El formato seleccionado para el almacenamiento es CSV, lo que facilita la manipulación y el análisis posterior de los datos. Amazon S3 proporciona durabilidad y escalabilidad, asegurando un acceso rápido y confiable a los datos almacenados.
 
En resumen, la arquitectura del proyecto se estructura de manera que aprovecha al máximo los servicios gestionados de AWS. Desde la obtención de datos con Jupyter Notebooks y la API de CoinGecko, pasando por el análisis en tiempo real en Kinesis, hasta el almacenamiento persistente en S3, cada componente contribuye a una solución completa y eficiente para el análisis continuo de precios de criptomonedas en la nube de AWS.



## Ejecución del proyecto

Con el fin de que el proyecto sea fácilmente reproducible, indicaremos paso a paso a modo de tutorial todas las configuraciones y pasos necesarios para poder reproducir la totalidad del proyecto.
 
Como primer paso crearemos el Clúster de AWS y lo configuraremos para que contenga la aplicación de Jyper Notebooks, adicionalmente es necesario crear un bucket para almacenar los datos procesados y tener persistencia sobre los mismos. Este bucket puede ser el mismo utilizado al momento de configurar Jupyter.
 
Como siguiente paso crearemos una instancia de Kinesis que utilizaremos como Data Stream, esta instancia recibirá los datos vivos que se capturen por medio de un script que estará corriendo en un notebook de Jupyter.

 ![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/95817c92-4c78-4f08-b4fa-b7acfa6bf33e)

Ahora bien, ya creado nuestro Data Stream procederemos a entrar a Jupyter Notebooks, con el fin de ejecutar el script que nos permitirá obtener los datos vivos es necesario correr los siguientes códigos para las importaciones de las librerías necesarias: 

	!pip install requests
	!pip install boto3
	!pip install pandas
 
Ahora correremos el script, el código lo pueden encontrar con el nombre de “P3-producer.ipynb” en nuestro GitHub: 
 https://github.com/jovillarrealm/jovillarrealm-st0263/blob/main/p3/

Una vez ejecutado el código veremos algo como esto:
![image](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/d433e6cf-4d4b-400a-ac76-8b5fde424f0d)









