# Create an EFS and mount on EKS worker nodes

This document explains how to create an Amazon EFS filesystem and mount on Amazon EKS worker nodes. This is then used for training of Machine Learning across distributed nodes.

The instructions are explained use [AWS Console](https://us-west-2.console.aws.amazon.com/efs/v2/home) in the `us-west-2` region.

1. Click on `Create file system`.

	1. Under `Configure file system access` select the VPC used for creating EKS Worker Nodes. If your cluster was created using eksctl as explained in [eks-gpu.md], then it would have `eks-ctl-gpu-cluster` in the VPC's name. This can be confirmed by looking into at the VPC ID attribute of the worker node in EC2 console. Click on `Next` after selecting the VPC.

	1. Under `Configure optional settings`, add a key with name `Arun` (change to your name) and value as `EFS`. Take everything as default. Click on `Next`.

	1. Review and click on `Create file system`.

1. Find the security group for the created file system and open up port 2049. This is needed because EFS gets mounted over NFS and the NFS server listens on well known port 2049.

1. Attach this file system to each worker nodes. Login to each worker node.
Click on the created EFS. Under `File system access`, click on `Amazon EC2 mount instructions`. Follow the steps in `Mounting your filesystem` section to mount the created filesystem. Use the `NFS client` to mount the filesystem. This would look like:

	```
	sudo mkdir efs
	sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-xxxxxxx.efs.<region>.amazonaws.com:/ efs
	```
