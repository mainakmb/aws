data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster"{
  name = module.eks.cluster_id
}

data "aws_availability_zones" "available" {}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-eks-vpc"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  enable_vpn_gateway   = true
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
}

module "eks" {
  source                          = "terraform-aws-modules/eks/aws"
  cluster_version                 = var.cluster_version
  cluster_name                    = var.cluster_name
  subnets                         = module.vpc.private_subnets
  vpc_id                          = module.vpc.vpc_id
  cluster_endpoint_private_access = true

  node_groups = {
    example = {
      desired_capacity = 1
      max_capacity     = 5
      min_capacity     = 1

      instance_type = var.instance_type
      k8s_labels = {
        Environment = "test"
        GithubRepo  = "terraform-aws-eks"
        GithubOrg   = "terraform-aws-modules"
      }
      additional_tags = {
        ExtraTag = "example"
      }
      # taints = [
      #   {
      #     key    = "dedicated"
      #     value  = "gpuGroup"
      #     effect = "NO_SCHEDULE"
      #   }
      # ]
    }
  }
  # map_roles    = var.map_roles
  # map_users    = var.map_users
  # map_accounts = var.map_accounts
}

resource "helm_release" "loki-stack" {
  name       = "loki"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki-stack"

  set {
    name  = "grafana.enabled"
    value = "true"
  }

  set {
    name  = "prometheus.enabled"
    value = "true"
  }

  set {
    name  = "prometheus.alertmanager.persistentVolume.enabled"
    value = "false"
  }

  set {
    name  = "prometheus.server.persistentVolume.enabled"
    value = "false"
  }
}