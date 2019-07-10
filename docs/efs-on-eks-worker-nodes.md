# Create an EFS and mount on EKS worker nodes

This document explains how to create an Amazon EFS filesystem and mount on Amazon EKS worker nodes. This is then used for training of Machine Learning across distributed nodes.

The instructions are explained using [AWS Console](https://console.aws.amazon.com/efs/home).

1. Click on `Create file system`.

	1. Under `Configure file system access` select the VPC used for creating EKS Worker Nodes. If your cluster was created using eksctl as explained in [Create GPU-enabled Amazon EKS cluster](eks-gpu.md), then it would have `eksctl-kubeflow-aws-cluster` in the VPC's name. This can be confirmed by looking into at the VPC ID attribute of the worker node in EC2 console. Click on `Next Step` after selecting the VPC.

	2. Take defaults in `Configure optional settings` and click on `Next Step`.

	3. Review and click on `Create File System`.

2. EFS gets mounted over NFS and the NFS server listens on well known port 2049. This port needs to be explicitly opened up in EFS security group. Security group for the created file system is shown in the EFS console. In [AWS Console](https://console.aws.amazon.com/ec2/home?#SecurityGroups:sort=groupId), add an inbound rule with a `Custom TCP Rule`, specify port 2049, and change the source to `Anywhere`.

3. Attach this file system to each worker nodes. Login to each worker node.
Click on the created EFS. Under `File system access`, click on `Amazon EC2 mount instructions (from local VPC)`. Setup your EC2 instance:

	```
	sudo yum install -y amazon-efs-utils
	```

	Follow the steps in `Mounting your filesystem` section to mount the created filesystem. Use the `NFS client` to mount the filesystem. This would look like:

	```
	sudo mkdir efs
	sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-xxxxxxx.efs.<region>.amazonaws.com:/ efs
	```
