sudo snap install microk8s --classic
sudo usermod -a -G microk8s $(whoami)
sudo chown -R $(whoami) ~/.kube
newgrp microk8s