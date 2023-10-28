## Información de la materia
	ST0263 Tópicos especiales en telemática
 
## Integrantes del equipo
	Jorge A. Villarreal
 	Daniel Gonzalez
  	Martin Villegas

## Profesor
	Edwin Nelson Montoya Munera, emontoya@eafit.edu.co

## Nombre del proyecto
	Reto 4 Tópicos Especiales en Telemática

## Objetivos logrados en el proyecto

1. Desplegamos con éxito un clúster de Kubernetes utilizando el software microk8s en cuatro máquinas virtuales en Google Cloud Platform (GPC), cumpliendo con el requisito de no utilizar un clúster como servicio administrado por GCP.
2. Implementamos un balanceador de cargas y garantizamos alta disponibilidad en la capa de aplicación, base de datos y almacenamiento.
3. Desarrollamos una aplicación Wordpress en la nube GCP, alojada en un clúster de Kubernetes basado en microk8s.
4. Creamos un repositorio en GitHub para el reto4 con todas las fuentes de la aplicación, adaptación, documentación, y otros componentes relacionados.
5. Logramos configurar un servidor de NFS para ser usado como volumen por microk8s según su [tutorial](https://microk8s.io/docs/nfs).

## Objetivos No Logrados:
1. A pesar de tener funcionando la base de datos y la aplicación de wordpress, la conexión entre ellas falla.
2. Un nombre de dominio.


![imagen](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/88699002/acdff9d7-7655-4b73-a57b-ef3fab5ca293)



## Instrucciones configuracion y creación proyecto

#### Primero se crean las VM de los nodos y del líder con E2-MICRO Y Ubuntu 22.04 y se corre:
    
    
	sudo snap refresh
    
	
#### En cada maquina instalamos el microk8s con : 
    
	sudo snap install microk8s --classic
    

#### Además corremos el siguiente comando para otorgar permisos de superusuario y no tener que estar utilizando sudo para cada comando que se corre:
	
    sudo usermod -a -G microk8s $(whoami)
    

#### En la máquina que va a ser el líder (control plane) usamos el código (se corre por cada máquina nueva): 
    
	microk8s add-node
![WhatsApp Image 2023-10-20 at 7 33 58 PM](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/20dc0853-5f27-4be2-90d4-590616f52d52)

	
#### De acá obtenemos los códigos únicos para más adelante utilizar en cada máquina y poderla conectar al líder.


#### Cuando se tienen los códigos necesarios se corre la siguiente línea en cada máquina para conectarse al líder:
    
	microk8s join 10.128.0.11:25000/834739147cdfa9bb857e7b1f19b0de70/d997f5f24439
    


#### Luego para revisar que los nodos ya hacen parte del cluster, usamos el código:
    
	microk8s kubectl get nodes
    
![Screen Shot 2023-10-26 at 12 07 22 AM](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/cde55766-a40e-49b2-bf76-d86004127d9e)


#### En el nodo principal creamos la base de datos definiendo una configuración por medio de un archivo yaml y luego aplicamos los cambios de esa configuración por medio del siguiente comando: 
    
	microk8s kubectl apply -f mysql-statefulset.yaml
    


#### Luego para ver las bases de datos que tenemos corremos el siguiente comando (debe mostrar 2 por configurar 2 réplicas):
    
	microk8s kubectl get pods
    


#### Y para ver todos los servicios que se están corriendo en el cluster lo hacemos con el comando (My service es el load balancer):
    
	microk8s kubectl get svc
    
![WhatsApp Image 2023-10-25 at 11 52 54 PM](https://github.com/jovillarrealm/jovillarrealm-st0263/assets/60147106/bc52598b-d779-4b87-bfce-09a6a6a24b5f)



#### NFS

El directorio que va a ser usado es `/srv/nfs` que va a ser expuesto a la subred 10.128.0.0/24 pero debería cambiarse a la subred en la que esté trabajando el cluster (en este caso la VPC de GCP). La siguiente configuración debe hacerse en el servidor que vaya a servir de almacenamiento.

Install kubernetes CSI driver

    sudo apt-get install -y nfs-kernel-server
    sudo mkdir -p /srv/nfs
    sudo chown nobody:nogroup /srv/nfs
    sudo chmod 0777 /srv/nfs
    sudo mv /etc/exports /etc/exports.bak

    echo '/srv/nfs 10.128.0.0/24(rw,sync,no_subtree_check)' | sudo tee /etc/exports

    sudo systemctl restart nfs-kernel-server
    microk8s enable helm3
    microk8s helm3 repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
    microk8s helm3 repo update
    microk8s helm3 install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
        --namespace kube-system \
        --set kubeletDir=/var/snap/microk8s/common/var/lib/kubelet
    microk8s kubectl wait pod --selector app.kubernetes.io/name=csi-driver-nfs --for condition=ready --namespace kube-system
    microk8s kubectl get csidrivers

Tambien vamos a hacer un storage class para tener nfs en un servidor específico que vaya a ser usado, en este caso se necesita cambiar la IP Privada (de GCP, no en cluster) 10.128.0.47. (Este comando es para crear el archivo dinamicamente, pero ya también está creado).

    cat <<EOF > sc-nfs.yaml
    apiVersion: storage.k8s.io/v1
    kind: StorageClass
    metadata:
        name: nfs-csi
    provisioner: nfs.csi.k8s.io
    parameters:
        server: 10.128.0.47
        share: /srv/nfs
    reclaimPolicy: Delete
    volumeBindingMode: Immediate
    mountOptions:
        - hard
        - nfsvers=4.1
    EOF

Se aplica y se chequea

    microk8s kubectl apply -f - < sc-nfs.yaml
    microk8s kubectl get sc

#### BD

Para tener la base de datos vamos a necesitar un pv, pvc, configuración en forma de un ConfigMap, y un Deployment que va a ser expuesto de un servicio. Aquí se pueden crear los archivos correspondientes copiando lo siguiente. (Se omite el yaml del deployment dado que no requiere configurar).

    cat <<EOF > postgres-config.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: postgres-config
        labels:
            app: postgres
    data:
        POSTGRES_DB: postgresdb
        POSTGRES_USER: admin
        POSTGRES_PASSWORD: psltest

    EOF
    
    cat <<EOF > postgres-pv.yaml
    kind: PersistentVolume
    apiVersion: v1
    metadata:
        name: postgres-pv-volume  # Sets PV's name
        labels:
            type: local  # Sets PV's type to local
            app: postgres
    spec:
        storageClassName: manual
        capacity:
            storage: 5Gi # Sets PV Volume
        accessModes:
            - ReadWriteMany
        hostPath:
            path: "/mnt/data"
    EOF

    cat <<EOF > postgres-pvc.yaml
    kind: PersistentVolumeClaim
    apiVersion: v1
    metadata:
        name: postgres-pv-claim  # Sets name of PVC
        labels:
            app: postgres
    spec:
        storageClassName: manual
        accessModes:
            - ReadWriteMany  # Sets read and write access
        resources:
            requests:
                storage: 5Gi  # Sets volume size
    EOF

    cat <<EOF > postgres-service.yaml
    apiVersion: v1
    kind: Service
    metadata:
        name: postgres # Sets service name
        labels:
            app: postgres # Labels and Selectors
    spec:
        type: NodePort # Sets service type
        ports:
            - port: 5432 # Sets port to run the postgres application
        selector:
            app: postgres
    EOF

Y se crean las cosas

    microk8s kubectl apply -f postgres-config.yaml
    microk8s kubectl apply -f postgres-pv.yaml
    microk8s kubectl apply -f postgres-pvc.yaml
    microk8s kubectl apply -f postgres-deployment.yaml
    microk8s kubectl apply -f postgres-service.yaml

#### WordPress

Para tener wordpress vamos a usar cositas bonitas SIN EL LOAD BALANCER AAAAAAAAAAAAAAAAAAAAA

    cat <<EOF > wordpress-service.yaml
    kind: Service
    apiVersion: v1
    metadata:
      name: wordpress-service
    spec:
      type: NodePort
      selector:
        app: wordpress
    ports:
      - name: http
        protocol: TCP
        port: 80
        targetPort: 80
        nodePort: 30007
    EOF
Y luego se construye con el deployment, servicio e ingress.


La conexión entre wordpress y postgres está mal enotnces para reproducir la pantalla mostrada al principio solo se suben los servicios necesarios para wordpress. 

    microk8s kubectl apply -f wordpress-nfs-pvc.yaml
    microk8s kubectl apply -f wordpress-deployment.yaml
    microk8s kubectl describe pvc wordpress-nfs-pvc
    microk8s kubectl apply -f wordpress-service.yaml
    microk8s kubectl apply -f wordpress-ingress.yaml
    microk8s kubectl get all -o wide

Para un postgres que sirve autocontenido está

    microk8s kubectl apply -f postgres-pv.yaml
    microk8s kubectl apply -f postgres-pvc.yaml
    microk8s kubectl apply -f postgres-deployment.yaml
    microk8s kubectl apply -f postgres-service.yaml

Si se necesita borrar

    microk8s kubectl delete ingress wordpress-ingress
    microk8s kubectl delete svc wordpress-service
    microk8s kubectl delete deployment wordpress-deployment
    microk8s kubectl delete pvc wordpress-nfs-pvc

    microk8s kubectl delete svc postgres-service
    microk8s kubectl delete deployment postgres
    microk8s kubectl delete pvc postgres-pv-claim
    microk8s kubectl delete pv postgres-pv-volume





## Referencias
	- https://microk8s.io/docs/nfs
 	- https://engr-syedusmanahmad.medium.com/wordpress-on-kubernetes-cluster-step-by-step-guide-749cb53e27c7
  	- https://www.youtube.com/watch?v=DCoBcpOA7W4
