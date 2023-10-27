Para tener la base de datos vamos a necesitar un pv, pvc, configuración en forma de un ConfigMap, y un Deployment
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

    kubectl apply -f postgres-config.yaml 


Para configurar el pv y pvc de la base de datos
    cat <<EOF > postgres-pvc-pv.yaml

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
    ---
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

    kubectl apply -f postgres-pvc-pv.yaml 

Para el deployment de la base de datos que usa los comandos anteriores

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

    kubectl apply -f postgres-deployment.yaml
Ya por último podemos crear el servicio que va a estar disponible al cluster :3
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

    kubectl apply -f postgres-service.yaml
Para tener wordpress vamos a usar cositas bonitas SIN EL LOAD BALANCER AAAAAAAAAAAAAAAAAAAAA


