# Reto 4 Topicos Especiales en Telemática

## Integrantes del equipo
	Jorge A. Villarreal
 	Daniel Gonzalez
  	Martin Villegas

## Objetivos logrados en el proyecto

1. Desplegamos con éxito un clúster de Kubernetes utilizando el software microk8s en cuatro máquinas virtuales en Google Cloud Platform (GPC), cumpliendo con el requisito de no utilizar un clúster como servicio administrado por GCP.
2. Implementamos un balanceador de cargas y garantizamos alta disponibilidad en la capa de aplicación, base de datos y almacenamiento.
3. Desarrollamos una aplicación Wordpress en la nube GCP, alojada en un clúster de Kubernetes basado en microk8s.
4. Creamos un repositorio en GitHub para el reto4 con todas las fuentes de la aplicación, adaptación, documentación, y otros componentes relacionados.
5. Logramos configurar un servidor de NFS para ser usado como volumen por microk8s según su [tutorial](https://microk8s.io/docs/nfs).

## Objetivos No Logrados:
1. No pudimos exponer una IP externa para acceder directamente a la aplicación desde un navegador externo.
2. No Permitimos el aumento dinámico de nodos en el clúster Kubernetes, lo que no nos permitirá escalar nuestra aplicación de manera efectiva.
3. Debido a que no teníamos la IP externa no fue posible creamos un dominio para el servicio.





## Instrucciones configuracion y creación proyecto

#### Primero se crean las VM de los nodos y del líder con E2-MICRO Y Ubuntu 22.04 y se corre:
    
    
	sudo snap refresh
    
	
#### En cada maquina instalamos el microk8s con : 
    
	sudo snap install microk8s --classic
    

#### Además corremos el siguiente comando para otorgar permisos de superusuario y no tener que estar utilizando sudo para cada comando que se corre:
	
    sudo usermod -a -G microk8s $(whoami)
    

#### En la máquina que va a ser el líder (control plane) usamos el código (se corre por cada máquina nueva): 
    
	microk8s add-node
    
	
#### De acá obtenemos los códigos únicos para más adelante utilizar en cada máquina y poderla conectar al líder.


#### Cuando se tienen los códigos necesarios se corre la siguiente línea en cada máquina para conectarse al líder:
    
	microk8s join 10.128.0.11:25000/834739147cdfa9bb857e7b1f19b0de70/d997f5f24439
    


#### Luego para revisar que los nodos ya hacen parte del cluster, usamos el código:
    
	microk8s kubectl get nodes
    


#### En el nodo principal creamos la base de datos definiendo una configuración por medio de un archivo yaml y luego aplicamos los cambios de esa configuración por medio del siguiente comando: 
    
	microk8s kubectl apply -f mysql-statefulset.yaml
    


#### Luego para ver las bases de datos que tenemos corremos el siguiente comando (debe mostrar 2 por configurar 2 réplicas):
    
	microk8s kubectl get pods
    


#### Y para ver todos los servicios que se están corriendo en el cluster lo hacemos con el comando (My service es el load balancer):
    
	microk8s kubectl get svc
    


#### Luego en el plane se hacen unos archivos de configuración yaml para el pvc del wordpress para luego proceder a crear el wordpress como tal. Luego de tener el yaml para el pvc corremos este comando:
    
	kubectl apply -f wordpress-pvc.yaml
    

#### Y para correr el archivo de configuraciones del wordpress utilizamos lo siguiente:
    
	microk8s kubectl apply -f wordpress-deployment.yaml


#### Luego se corren los servicios de configuración de la siguiente forma

    microk8s kubectl apply -f mysql-secret.yaml
    microk8s kubectl apply -f mysql-pv-pvc.yaml
    microk8s kubectl apply -f mysql-statefulset.yaml
    microk8s kubectl apply -f mysql-service.yaml
    microk8s kubectl apply -f wordpress-pv-pvc.yaml
    microk8s kubectl apply -f wordpress-deployment.yaml
