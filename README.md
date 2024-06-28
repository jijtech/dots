placeholder md
https://nixos.wiki/wiki/Kubernetes

https://rzetterberg.github.io/kubernetes-nixos.html

https://nixos.wiki/wiki/NixOps

Before you proceed, be aware that this document is peppered with

    🔴 hard requirements that must be met to ensure k8s components function
    🟡 official recommendations (from the kubernetes.io docs ) that should be followed whenever possible to reduce the risk of any incompatibilities
    🟠 best practices that are not required, but should be implemented to avoid long-term issues

Some of the examples on this page work across al *nix systems. Others (.e.g apt-get) are Debian-based.
System Requirements

This section contains overall system requirements for each machine that is going to be part of a k8s cluster.
For network requirements, skip ahead to the network toplogy section.
(https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin )

🟡 One more machines running one of:

    Ubuntu 16.04+
    Debian 9+
    CentOS 7+
    Red Hat Enterprise Linux (RHEL) 7+
    Fedora 25+
    HypriotOS v1.0.1+

(you could technically pick something else, but keep in mind that the official docs revolve around configuring systems based on the distros above)

🔴 2 GB or more of RAM per machine
(any less and there won't be any headroom for meaningful workloads)

🔴 2 CPUs/vCPUs or more per machine
(extremely important for master nodes as k8s some control plane componets will not run with less)

🟡 50 GB or more of storage per machine
(while slightly overkill, extending volumes is not trivial depending on the OS)
Software Prerequisites

This section contains prerequisite configuration and package installation that must be done on each machine.
Disable swap

🔴 The swap partition must be turned off for the kubelet to work properly

    Run swapoff -a as root
    Run nano /etc/fstab (or any other editor) as root and comment out the swap partition

alg@c1-master1:~$ free
              total        used        free      shared  buff/cache   available
Mem:        2040788      171628      882724         756      986436     1709612
Swap:             0           0           0
                              ↑ 0 used

Install runtime (docker*)

🔴 A runtime is needed so k8s can actually run containers
(* de facto choice for now, keep in mind that docker CAN and will most likely be swapped with a different runtime in the future)

Follow the official Install Docker Engine guide for your distro of choice. However,

on a Debian-based installation, use the the docker.io package provided by Debian rather than the official Docker repositories.
(read here for an explanation on why)

    Run sudo apt-get update to update your package list
    Run sudo apt-get install -y docker.io to install the docker version provided by the official Debian repositories

Configure docker daemon

🟡 overlay2 is the preferred storage driver, for all currently supported Linux distributions, and requires no extra configuration
(https://docs.docker.com/storage/storagedriver/select-storage-driver/ )
🟠 Set the log size to a reasonable size — otherwise containers that are very verbose with their logging can easily eat up space on each node

    Run the command bellow to add a daemon.json configuration

sudo bash -c 'cat > /etc/docker/daemon.json <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "500m"
  },
  "storage-driver": "overlay2"
}
EOF'

    Run sudo systemctl daemon-reload to reload systemd config
    Run sudo systemctl restart docker.service to restart docker service
    Run sudo systemctl enable docker.service to ensure docker starts at system startup

Install kubeadm, kubelet and kubectl

These three packages are required on all machine to bootstrap a cluster the kubeadm way:

    🟡 kubeadm: the command line utility that we use to bootstrap our cluster (e.g. initialize/join a cluster)
    🔴 kubelet: the component that than runs on every node and does things like starting pods and containers (i.e. basically manages the workloads on the node)
    🔴 kubectl: the command line utility that we use to talk to our cluster

kubeadm will not manage the kubelet or kubectl versions that are installed — we need to match their version against the k8s masters we bootstrap with kubeadm.
We must use a kubectl version that is within one minor version difference of your cluster.
e.g. a v1.2 client should work with v1.1, v1.2, and v1.3 master. Using the latest version of kubectl helps avoid unforeseen issues
(https://kubernetes.io/docs/tasks/tools/install-kubectl/#before-you-begin )

🔴 First, update the package list to include the k8s source list.

    Run sudo apt-get update && sudo apt-get install -y apt-transport-https curl to get the necessary tools
    Run curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - to retrieve the apt GPG key
    Add the k8s sources list

sudo bash -c 'cat <<EOF | tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF'

    Run sudo apt-get update again to update your package list

🔴 After updating your package list, you should be able to use your package manager to inspect which versions of these packages are currently available and install them.

    Run apt-cache policy kubelet | head -n 20 (head to limit output)

alg@c1-master1:~$ apt-cache policy kubelet | head -n 20 
kubelet:
  Installed: 1.20.2-00
  Candidate: 1.20.2-00
  Version table:
 *** 1.20.2-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
        100 /var/lib/dpkg/status
     1.20.1-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.20.0-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.19.7-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.19.6-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.19.5-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.19.4-00 500
        500 https://apt.kubernetes.io kubernetes-xenial/main amd64 Packages
     1.19.3-00 500

    Pick the version that you want to install

VERSION=1.20.2-00

    Run apt-get install to install the packages

sudo apt-get install -y kubelet=$VERSION kubeadm=$VERSION kubectl=$VERSION

    Enable the kubelete.service

sudo systemctl enable kubelet.service

    [ Kubelet service is crashed, that's normal, we haven't initialized anything yet ]

alg@c1-node1:~/k8s$ sudo systemctl status kubelet.service
● kubelet.service - kubelet: The Kubernetes Node Agent
   Loaded: loaded (/lib/systemd/system/kubelet.service; enabled; vendor preset: enabled)
  Drop-In: /etc/systemd/system/kubelet.service.d
           └─10-kubeadm.conf
   Active: activating (auto-restart) (Result: exit-code) since Thu 2021-02-04 11:39:50 UTC; 3s ago
     Docs: https://kubernetes.io/docs/home/
  Process: 22716 ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS (code=exited, status=255) Main PID: 22716 (code=exited, status=255)

    Enable autocomplete for kubectl to make our life easier

echo "source <(kubectl completion bash)" >> ~/.bashrc
source ~/.bashrc

Mark packages as non-upgradable

🔴 Kubernetes can be upgraded with zero-downtime as long as is in charge of managing its own upgrades*

    Run sudo apt-mark hold kubelet kubeadm kubectl to tell the package manager to not manage upgrades for these packages

(* this is true when bootstrapping a cluster via kubeadm — in other deployment types, you might need to manage package upgrades manually)
Network Requirements

This network covers basic network considerations and configuration to ensure proper operation of kube-proxy .
MAC address and product UUID

🔴 Ensure that the MAC address of every network interface and product UUIDs are unique on every node

    Run ip link or ifconfig -a to get the MAC address of each interface
    Run sudo cat /sys/class/dmi/id/product_uuid to get product UUID
    e.g. C0746D4F-FD5D-A64B-84D4-E7D01206C0E2

alg@c1-node1:~$ ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether 08:00:27:e1:b7:b8 brd ff:ff:ff:ff:ff:ff
                       ↑
                  MAC address

3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether 08:00:27:14:0b:18 brd ff:ff:ff:ff:ff:ff
4: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default
    link/ether 02:42:79:db:3a:57 brd ff:ff:ff:ff:ff:ff

Network connectivity and hostfile

🔴 Ensure network connectivity between nodes on the desidred network interfaces

alg@c1-master1:~$ ping 192.168.56.11
PING 192.168.56.11 (192.168.56.11) 56(84) bytes of data.
64 bytes from 192.168.56.11: icmp_seq=1 ttl=64 time=0.258 ms
64 bytes from 192.168.56.11: icmp_seq=2 ttl=64 time=1.81 ms
64 bytes from 192.168.56.11: icmp_seq=3 ttl=64 time=0.672 ms
64 bytes from 192.168.56.11: icmp_seq=4 ttl=64 time=0.505 ms
64 bytes from 192.168.56.11: icmp_seq=5 ttl=64 time=0.430 ms

🟠 Set up the /etc/hosts file accordingly

alg@c1-master1:/etc/kubernetes/manifests$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 c1-master1

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

# c1 Kubernetes cluster
192.168.56.11 c1-node1
192.168.56.12 c1-node2

Let iptables see bridged traffic

For the cluster network to work properly, we need to ensure that br_netfilter is loaded and that iptables are allowed to see bridged traffic on each node.

🔴 Make sure that the br_netfilter module is loaded

sudo bash -c 'cat <<EOF | tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF'

🔴 Make sure that net.bridge.bridge-nf-call-iptables is set to 1 in the sysctl config so that each node's ipables can see bridged traffic

sudo bash -c 'cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF'

Run sysctl --system to apply the new configuration without rebooting.
Open required ports

🔴 At a minimum, ensure the following ports are open

Control plane node(s) i.e. master(s)
	Purpose 	Used By
TCP (inbound) 6443 	Kubernetes API server 	all nodes
TCP (inbound) 2379-2380 	etcd server client API 	kube-apiserver, etcd
TCP (inbound) 10250 	kubelet API 	self, control plane nodes
TCP (inbound) 10251 	kube-scheduler 	self
TCP (inbound) 10252 	kube-controller-manager 	self

Worker node(s)
	Purpose 	Used By
TCP (inbound) 10250 	kubelet API 	self, control plane nodes
TCP (inbound) 30000-32767 	etcd server client API 	self

🟡 Based on the pod network plugin that we choose, additional ports might be required
Bootstrap Cluster with kubeadm

(assumes you've picked Calico for CNI)

This section walks you initializing the k8s control plane (i.e. master) and joining a worker node via kubeadm.
Initialize control plane

    Download the CNI (i.e. pod network) manifest (i.e. Calico in our case)

(for now we only save the manifest to have it handy, we will deploy the actual pod network once we're done bootstrapping the control plane)

curl https://docs.projectcalico.org/manifests/calico.yaml -O k8s/calico.yaml

    Initialize the control plane with kubeadm init
    in this example the --api-server-advertise-address is used as we do not use to wish the default network interface of the node to advertise the API server on

alg@c1-master1:~$ sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --apiserver-advertise-address=192.168.56.10
[init] Using Kubernetes version: v1.20.2
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "ca" certificate and key
[certs] Generating "apiserver" certificate and key
[certs] apiserver serving cert is signed for DNS names [c1-master1 kubernetes kubernetes.default kubernetes.default.svc kubernetes.default.svc.cluster.local] and IPs [10.96.0.1 192.168.56.10]
[certs] Generating "apiserver-kubelet-client" certificate and key
[certs] Generating "front-proxy-ca" certificate and key
[certs] Generating "front-proxy-client" certificate and key
[certs] Generating "etcd/ca" certificate and key
[certs] Generating "etcd/server" certificate and key
[certs] etcd/server serving cert is signed for DNS names [c1-master1 localhost] and IPs [192.168.56.10 127.0.0.1 ::1]
[certs] Generating "etcd/peer" certificate and key
[certs] etcd/peer serving cert is signed for DNS names [c1-master1 localhost] and IPs [192.168.56.10 127.0.0.1 ::1]
[certs] Generating "etcd/healthcheck-client" certificate and key
[certs] Generating "apiserver-etcd-client" certificate and key
[certs] Generating "sa" key and public key
[kubeconfig] Using kubeconfig folder "/etc/kubernetes"
[kubeconfig] Writing "admin.conf" kubeconfig file
[kubeconfig] Writing "kubelet.conf" kubeconfig file
[kubeconfig] Writing "controller-manager.conf" kubeconfig file
[kubeconfig] Writing "scheduler.conf" kubeconfig file
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Starting the kubelet
[control-plane] Using manifest folder "/etc/kubernetes/manifests"
[control-plane] Creating static Pod manifest for "kube-apiserver"
[control-plane] Creating static Pod manifest for "kube-controller-manager"
[control-plane] Creating static Pod manifest for "kube-scheduler"
[etcd] Creating static Pod manifest for local etcd in "/etc/kubernetes/manifests"
[wait-control-plane] Waiting for the kubelet to boot up the control plane as static Pods from directory "/etc/kubernetes/manifests". This can take up to 4m0s[apiclient] All control plane components are healthy after 22.506452 seconds
[upload-config] Storing the configuration used in ConfigMap "kubeadm-config" in the "kube-system" Namespace
[kubelet] Creating a ConfigMap "kubelet-config-1.20" in namespace kube-system with the configuration for the kubelets in the cluster
[upload-certs] Skipping phase. Please see --upload-certs
[mark-control-plane] Marking the node c1-master1 as control-plane by adding the labels "node-role.kubernetes.io/master=''" and "node-role.kubernetes.io/control-plane='' (deprecated)"
[mark-control-plane] Marking the node c1-master1 as control-plane by adding the taints [node-role.kubernetes.io/master:NoSchedule]
[bootstrap-token] Using token: l1kdss.3mpkkuczimex6d25
[bootstrap-token] Configuring bootstrap tokens, cluster-info ConfigMap, RBAC Roles
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to get nodes
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to post CSRs in order for nodes to get long term certificate credentials
[bootstrap-token] configured RBAC rules to allow the csrapprover controller automatically approve CSRs from a Node Bootstrap Token
[bootstrap-token] configured RBAC rules to allow certificate rotation for all node client certificates in the cluster
[bootstrap-token] Creating the "cluster-info" ConfigMap in the "kube-public" namespace
[kubelet-finalize] Updating "/etc/kubernetes/kubelet.conf" to point to a rotatable kubelet client certificate and key
[addons] Applied essential addon: CoreDNS
[addons] Applied essential addon: kube-proxy

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.56.10:6443 --token l1kdss.3mpkkuczimex6d25 \
    --discovery-token-ca-cert-hash sha256:c8085f1df905c78cbafca7abd18cedc89a5b8c72f5e5dbd84d3f923829489d40

    Set up configuration for kubectl
    (from this point on we can use kubectl to interact with our cluster)

alg@c1-master1:~$ mkdir -p $HOME/.kube
alg@c1-master1:~$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
alg@c1-master1:~$ sudo chown $(id -u):$(id -g) $HOME/.kube/config

    Deploy pod network
    (with the manifest we've downloaded in step 1)

alg@c1-master1:~$ kubectl apply -f k8s/calico.yaml
configmap/calico-config created
customresourcedefinition.apiextensions.k8s.io/bgpconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/bgppeers.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/blockaffinities.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/clusterinformations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/felixconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/globalnetworksets.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/hostendpoints.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamblocks.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamconfigs.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ipamhandles.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/ippools.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/kubecontrollersconfigurations.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networkpolicies.crd.projectcalico.org created
customresourcedefinition.apiextensions.k8s.io/networksets.crd.projectcalico.org created
clusterrole.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrolebinding.rbac.authorization.k8s.io/calico-kube-controllers created
clusterrole.rbac.authorization.k8s.io/calico-node created
clusterrolebinding.rbac.authorization.k8s.io/calico-node created
daemonset.apps/calico-node created
serviceaccount/calico-node created
deployment.apps/calico-kube-controllers created
serviceaccount/calico-kube-controllers created
poddisruptionbudget.policy/calico-kube-controllers created

    Verify that system pods are running

alg@c1-master1:~$ kubectl get pods --all-namespaces
NAMESPACE     NAME                                       READY   STATUS    RESTARTS   AGE
kube-system   calico-kube-controllers-744cfdf676-7psbp   1/1     Running   0          88s
kube-system   calico-node-sgdsw                          1/1     Running   0          88s
kube-system   coredns-74ff55c5b-vr45f                    1/1     Running   0          15m
kube-system   coredns-74ff55c5b-z7664                    1/1     Running   0          15m
kube-system   etcd-c1-master1                            1/1     Running   0          15m
kube-system   kube-apiserver-c1-master1                  1/1     Running   0          15m
kube-system   kube-controller-manager-c1-master1         1/1     Running   0          15m
kube-system   kube-proxy-9kk8l                           1/1     Running   0          15m
kube-system   kube-scheduler-c1-master1                  1/1     Running   0          15m

    Verify node status

alg@c1-master1:~$ kubectl get nodes
NAME         STATUS   ROLES                  AGE   VERSION
c1-master1   Ready    control-plane,master   16m   v1.20.2

    Check the kubeconfig files

alg@c1-master1:~$ ls /etc/kubernetes/
admin.conf  controller-manager.conf  kubelet.conf  manifests  pki  scheduler.conf

    Check the individual control plane components that make up the master node itself

alg@c1-master1:~$ ls /etc/kubernetes/manifests/
etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml

    Check that the kubelet service is now up and running

alg@c1-master1:~$ sudo systemctl status kubelet.service
● kubelet.service - kubelet: The Kubernetes Node Agent
   Loaded: loaded (/lib/systemd/system/kubelet.service; enabled; vendor preset: enabled)
  Drop-In: /etc/systemd/system/kubelet.service.d
           └─10-kubeadm.conf
   Active: active (running) since Thu 2021-02-04 10:32:26 UTC; 1h 6min ago
     Docs: https://kubernetes.io/docs/home/
 Main PID: 12651 (kubelet)
    Tasks: 15 (limit: 2317)
   CGroup: /system.slice/kubelet.service
           └─12651 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf --config=/var/lib

Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.006 [INFO][17784] ipam.go 970: Writing block in order to claim IPs block=192.168.19.64/26 handFeb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.021 [INFO][17784] ipam.go 983: Successfully claimed IPs: [192.168.19.67/26] block=192.168.19.6Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.021 [INFO][17784] ipam.go 706: Auto-assigned 1 out of 1 IPv4s: [192.168.19.67/26] handle="k8s-Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.021 [INFO][17784] ipam_plugin.go 255: Calico CNI IPAM assigned addresses IPv4=[192.168.19.67/2Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.024 [INFO][17741] k8s.go 372: Populated endpoint ContainerID="3e3ed06818a39f4595792d6da4f753ccFeb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.024 [INFO][17741] k8s.go 373: Calico CNI using IPs: [192.168.19.67/32] ContainerID="3e3ed06818Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.024 [INFO][17741] dataplane_linux.go 66: Setting the host side veth name to cali8acbc3564a9 CoFeb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.027 [INFO][17741] dataplane_linux.go 420: Disabling IPv4 forwarding ContainerID="3e3ed06818a39Feb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.058 [INFO][17741] k8s.go 400: Added Mac, interface name, and active container ID to endpoint CFeb 04 10:47:13 c1-master1 kubelet[12651]: 2021-02-04 10:47:13.095 [INFO][17741] k8s.go 474: Wrote updated endpoint to datastore ContainerID="3e3ed06818a39f4

Join worker nodes

    Retrieve an existing join token
    (this needs to be ran on a control plane node)

alg@c1-master1:~$ kubeadm token list
TOKEN                     TTL         EXPIRES                USAGES                   DESCRIPTION                                                EXTRA GROUPS
l1kdss.3mpkkuczimex6d25   21h         2021-02-05T10:32:25Z   authentication,signing   The default bootstrap token generated by 'kubeadm init'.   system:bootstrappers:kubeadm:default-node-token

    Create a new token, if none are available
    (this needs to be ran on a control plane node)

alg@c1-master1:~$ kubeadm token create
p352ng.vlw4mvd0lwrjo8pz

    Get the CA (certificate authority) cert hash
    (this needs to be ran on a control plane node)

alg@c1-master1:~$ openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //'
c8085f1df905c78cbafca7abd18cedc89a5b8c72f5e5dbd84d3f923829489d40

    Join worker node (with our new token)

alg@c1-node1:~$ sudo kubeadm join 192.168.56.10:6443 \
> --token p352ng.vlw4mvd0lwrjo8pz \
> --discovery-token-ca-cert-hash sha256:c8085f1df905c78cbafca7abd18cedc89a5b8c72f5e5dbd84d3f923829489d40
[preflight] Running pre-flight checks
[preflight] Reading configuration from the cluster...
[preflight] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -o yaml'
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Starting the kubelet
[kubelet-start] Waiting for the kubelet to perform the TLS Bootstrap...

This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.

    Verify that the node joined successfully
    (this needs to be ran on a control plane node)

alg@c1-master1:~$ kubectl get nodes
NAME         STATUS   ROLES                  AGE     VERSION
c1-master1   Ready    control-plane,master   3h15m   v1.20.2
c1-node1     Ready    <none>                 94s     v1.20.2
