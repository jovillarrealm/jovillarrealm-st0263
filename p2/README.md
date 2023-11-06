## Información de la materia
	ST0263 Tópicos especiales en telemática
 
## Integrantes del equipo
	Jorge A. Villarreal
 	Daniel Gonzalez Bernal
  	Martin Villegas

## Profesor
	Edwin Nelson Montoya Munera, emontoya@eafit.edu.co

## Nombre del proyecto
	Reto 4 Tópicos Especiales en Telemática

## Objetivos logrados en el proyecto

1. Se creo y desplego con exito un cluster de Kubernetes utilizando servicios administrados por GCP (Google Cloud Platform).
2. Se configuro Wordpress, un NFS (Network File System) y una base de datos MySQL en el cluster
3. Asignamos una ip estatica para facilitar el ingreso al cluster desde un cliente externo.
4. Se asigno el dominio https://retouniversidadeafit.xyz/ a la IP del cluster.



## Objetivos No Logrados:
Todo el proyecto se logro




## Instrucciones configuracion y creación proyecto

Antes de comenzar
Si eres nuevo en Google Cloud, crea una cuenta para evaluar el rendimiento de nuestros productos en situaciones reales. Los clientes nuevos obtienen $300 en créditos gratuitos para ejecutar, probar e implementar cargas de trabajo.
En la página del selector de proyectos de la consola de Google Cloud, selecciona o crea un proyecto de Google Cloud.


Asegúrate de que la facturación esté habilitada para tu proyecto de Google Cloud.

##### En la consola de Google Cloud, activa Cloud Shell.

Activar Cloud Shell

En la parte inferior de la consola de Google Cloud, se inicia una sesión de Cloud Shell en la que se muestra una ventana de línea de comandos. Cloud Shell es un entorno de shell con Google Cloud CLI ya instalada y con valores ya establecidos para el proyecto actual. La sesión puede tardar unos segundos en inicializarse.

En Cloud Shell, habilita las API de administrador de GKE y Cloud SQL:

gcloud services enable container.googleapis.com sqladmin.googleapis.com
Configura tu entorno
En Cloud Shell, configura la región predeterminada para Google Cloud CLI:


gcloud config set compute/region region
Reemplaza lo siguiente:

region: Elige la región más cercana a ti. Por ejemplo, us-central1.
Configura la variable de entorno PROJECT_ID como el ID de tu proyecto de Google Cloud (project-id).


export PROJECT_ID=project-id
Descarga los archivos de manifiesto de la app desde el repositorio de GitHub:


    git clone https://github.com/jovillarrealm/jovillarrealm-st0263
Cambia al directorio con el archivo wordpress-persistent-disks:


	cd jovillarrealm-st0263/p2
Establece la variable de entorno WORKING_DIR:


    WORKING_DIR=$(pwd)
Para este instructivo, debes crear objetos de Kubernetes mediante archivos de manifiesto en formato YAML.

Crea un clúster de GKE
Debes crear un clúster de GKE para alojar tu contenedor de app de WordPress.

En Cloud Shell, crea un clúster de GKE llamado persistent-disk-tutorial:


    CLUSTER_NAME=persistent-disk-tutorial
gcloud container clusters create-auto $CLUSTER_NAME
Una vez creada, conéctate al clúster nuevo:


    gcloud container clusters get-credentials $CLUSTER_NAME --region REGION
Crea un PV y un PVC con el respaldo de Persistent Disk
Crear un PVC como almacenamiento requerido para WordPress GKE tiene un recurso StorageClass predeterminado instalado que te permite aprovisionar de manera dinámica los PV con el respaldo de Persistent Disk. Tienes que usar el archivo wordpress-volumeclaim.yaml a fin de crear los PVC necesarios para la implementación.

Con este archivo de manifiesto se describe un PVC que solicita 200 GB de almacenamiento. No se definió un recurso StorageClass en el archivo, por lo que este PVC usa el recurso predeterminado StorageClass para aprovisionar un PV con el respaldo de Persistent Disk.

En Cloud Shell, implementa el archivo de manifiesto:


    kubectl apply -f $WORKING_DIR/wordpress-volumeclaim.yaml
Puede tardar hasta diez segundos en aprovisionar el PV con el respaldo de Persistent Disk y vincularlo a tu PVC. Puedes verificar el estado con el siguiente comando:


    kubectl get persistentvolumeclaim
El resultado muestra una PersistentVolumeClaim con un estado de Pending, similar al siguiente:


#### NAME                    STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
    wordpress-volumeclaim   Pending                                      standard-rwo   5s
Este PersistentVolumeClaim permanece en el estado Pending hasta que lo uses más adelante en este instructivo.

##### Crea una instancia de Cloud SQL para MySQL
En Cloud Shell, crea una instancia llamada mysql-wordpress-instance:


    INSTANCE_NAME=mysql-wordpress-instance
gcloud sql instances create $INSTANCE_NAME
Agrega el nombre de la conexión de la instancia como una variable de entorno:


    export INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME \
    --format='value(connectionName)')
#### Crea una base de datos para que WordPress almacene sus datos:

    gcloud sql databases create wordpress --instance $INSTANCE_NAME
Crea un usuario de base de datos llamado wordpress y una contraseña para que WordPress se autentique en la instancia:


    CLOUD_SQL_PASSWORD=$(openssl rand -base64 18)
    gcloud sql users create wordpress --host=% --instance $INSTANCE_NAME \
    --password $CLOUD_SQL_PASSWORD
Si cierras tu sesión de Cloud Shell, perderás la contraseña. Anótala porque la necesitarás más adelante en este instructivo.
	
	echo $CLOUD_SQL_PASSWORD
Terminaste de configurar la base de datos para tu nuevo blog de WordPress.

Implementa WordPress
Antes de implementar WordPress, debes crear una cuenta de servicio. Debes crear un secreto de Kubernetes que contenga las credenciales de la cuenta de servicio y otro para las credenciales de la base de datos.

Configura una cuenta de servicio y crea secretos
Para permitir que tu app de WordPress acceda a la instancia de MySQL a través de un proxy de Cloud SQL, crea una cuenta de servicio:


    SA_NAME=cloudsql-proxy
gcloud iam service-accounts create $SA_NAME --display-name $SA_NAME
Agrega la dirección de correo electrónico de la cuenta de servicio como una variable de entorno:


    SA_EMAIL=$(gcloud iam service-accounts list \
    --filter=displayName:$SA_NAME \
    --format='value(email)')
Agrega la función cloudsql.client a tu cuenta de servicio:


    gcloud projects add-iam-policy-binding $PROJECT_ID \
    --role roles/cloudsql.client \
    --member serviceAccount:$SA_EMAIL
##### Crea una clave para la cuenta de servicio:


    gcloud iam service-accounts keys create $WORKING_DIR/key.json \
    --iam-account $SA_EMAIL
Este comando descarga una copia del archivo key.json.

#### Crea un secreto de Kubernetes para las credenciales de MySQL:


    kubectl create secret generic cloudsql-db-credentials \
    --from-literal username=wordpress \
    --from-literal password=$CLOUD_SQL_PASSWORD
Crea un secreto de Kubernetes para las credenciales de la cuenta de servicio:


    kubectl create secret generic cloudsql-instance-credentials \
    --from-file $WORKING_DIR/key.json

    
### Implementa WordPress
El siguiente paso es implementar tu contenedor de WordPress en el clúster de GKE.

Con el archivo de manifiesto wordpress_cloudsql.yaml, se describe una implementación que crea un solo pod, el cual ejecuta un contenedor con una instancia de WordPress. Este contenedor lee la variable de entorno WORDPRESS_DB_PASSWORD que contiene el secreto cloudsql-db-credentials que creaste.

Este archivo de manifiesto también configura el contenedor de WordPress para que se comunique con MySQL a través del proxy de Cloud SQL que se ejecuta en el contenedor del archivo adicional. El valor de la dirección del host se configura en la variable de entorno WORDPRESS_DB_HOST.

Para preparar el archivo de implementación, reemplaza la variable de entorno                            INSTANCE_CONNECTION_NAME:


    cat $WORKING_DIR/wordpress_cloudsql.yaml.template | envsubst > \
    $WORKING_DIR/wordpress_cloudsql.yaml
##### Implementa el archivo de manifiesto wordpress_cloudsql.yaml:


    kubectl create -f $WORKING_DIR/wordpress_cloudsql.yaml
La implementación de este archivo de manifiesto toma unos minutos mientras Persistent Disk se conecta al nodo de procesamiento.

Mira la implementación para ver el cambio de estado a running:


     kubectl get pod -l app=wordpress --watch
Cuando en el resultado se muestre un estado de Running, puedes continuar con el siguiente paso.


    NAME                     READY     STATUS    RESTARTS   AGE
    wordpress-387015-02xxb   2/2       Running   0          2m47s
Expón el servicio de WordPress
En el paso anterior, implementaste un contenedor de WordPress, pero actualmente, no se puede acceder a este desde fuera del clúster porque no tiene una dirección IP externa. Puedes exponer la app de WordPress al tráfico de Internet mediante la creación y la configuración de un servicio de Kubernetes con un balanceador de cargas externo adjunto. Para obtener más información sobre cómo exponer apps mediante servicios en GKE, consulta la guía práctica.

##### Crea un Service de type:LoadBalancer:


    kubectl create -f $WORKING_DIR/wordpress-service.yaml
La creación de un balanceador de cargas toma unos minutos.

Mira la implementación y espera a que el servicio tenga asignada una dirección IP externa:


    kubectl get svc -l app=wordpress --watch
Cuando en el resultado se muestre una dirección IP externa, puedes continuar con el siguiente paso. Ten en cuenta que tu IP externa es diferente en el siguiente ejemplo.


    NAME        CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
    wordpress   10.51.243.233   203.0.113.3    80:32418/TCP   1m
Toma nota del campo de dirección EXTERNAL_IP para usarlo luego.


## Video

https://www.youtube.com/watch?v=g1oVDbAZsP4



## Referencias

Todo el tutorial anterior esta basado en el tutorial de Google y solo realizamos cambios menores en algunos codigos:
- https://cloud.google.com/kubernetes-engine/docs/tutorials/persistent-disk?hl=es-419
