variable "region" {
    default     = "ap-south-1"
    description = "AWS Region"
}

variable "cluster_name" {
    default = "my-eks-cluster"
}

variable "cluster_version" {
    default = "1.19"
}