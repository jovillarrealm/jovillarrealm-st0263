
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
      image: postgres:10.1  # Sets Image
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

cat <<EOF > pvc-nfs.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: nfs-csi
    accessModes: [ReadWriteOnce]
    resources:
      requests:
        storage: 40Gi
EOF

cat <<EOF > wordpress-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress-deployment
spec:
  replicas: 4
  selector:
    matchLabels:
      app: wordpress
  template:
    metadata:
      labels:
        app: wordpress
    spec:
      containers:
      - name: wordpress
        image: wordpress:latest
        envFrom:
        - configMapRef:
          name: postgres-config
        ports:
        - containerPort: 80
        volumeMounts:
        - name: wordpress-nfs-pvc
          mountPath: /var/www/html
          subPath: wordpress
  volumes:
  - name: wordpress-nfs-pvc
    persistentVolumeClaim:
      claimName: wordpress-nfs-pvc
EOF

cat <<EOF > ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wordpress-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wordpress-service
            port:
              number: 80
EOF