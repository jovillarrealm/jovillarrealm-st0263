
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

Tambien vamos a hacer un storage class para tener nfs en un servidor específico que vaya a ser usado, en este caso se necesita cambiar la IP Privada (de GCP, no en cluster) 10.128.0.47

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

#### BD

Para tener la base de datos vamos a necesitar un pv, pvc, configuración en forma de un ConfigMap, y un Deployment que va a ser expuesto de un servicio. Aquí se pueden crear los archivos correspondientes copiando lo siguiente.

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



    cat <<EOF > postgres-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
        name: postgres  # Sets Deployment name
    spec:
        replicas: 1
        selector:
            matchLabels:
            app: postgres
        template:
            metadata:
            labels:
                app: postgres
            spec:
            containers:
                - name: postgres
                image: postgres:10.1 # Sets Image
                imagePullPolicy: "IfNotPresent"
                ports:
                    - containerPort: 5432  # Exposes container port
                envFrom:
                    - configMapRef:
                        name: postgres-config
                volumeMounts:
                    - mountPath: /var/lib/postgresql/data
                    name: postgredb
            volumes:
                - name: postgredb
                persistentVolumeClaim:
                    claimName: postgres-pv-claim

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
