provider "aws" {
  region = "us-east-1"
}

# -----------------------------------------------------------------------------
# VPC & Networking (The Foundation)
# -----------------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "govcon-saas-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

# -----------------------------------------------------------------------------
# Database: Aurora Serverless v2 (PostgreSQL)
# Per DevOps mandate: Scales to 0 when idle, supports pgvector natively.
# -----------------------------------------------------------------------------
resource "aws_rds_cluster" "govcon_aurora" {
  cluster_identifier      = "govcon-saas-db"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.3"
  database_name           = "govcondb"
  master_username         = "postgres"
  master_password         = var.db_password # Injected via TF_VAR_db_password
  skip_final_snapshot     = true
  
  vpc_security_group_ids  = [aws_security_group.db_sg.id]
  db_subnet_group_name    = module.vpc.database_subnet_group_name

  serverlessv2_scaling_configuration {
    max_capacity = 2.0
    min_capacity = 0.5
  }
}

resource "aws_rds_cluster_instance" "govcon_aurora_instance" {
  cluster_identifier = aws_rds_cluster.govcon_aurora.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.govcon_aurora.engine
  engine_version     = aws_rds_cluster.govcon_aurora.engine_version
}

# -----------------------------------------------------------------------------
# Compute: AWS Fargate (ECS)
# Per DevOps mandate: Serverless compute for Background Tasks & API
# -----------------------------------------------------------------------------
resource "aws_ecs_cluster" "govcon_cluster" {
  name = "govcon-saas-cluster"
}

resource "aws_ecs_task_definition" "backend_task" {
  family                   = "govcon-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${var.ecr_repo_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_rds_cluster.govcon_aurora.endpoint}:5432/govcondb" },
        { name = "GEMINI_API_KEY", value = var.gemini_api_key }
      ]
    }
  ])
}

# Variables
variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Google Gemini API Key for Entity Resolution"
  type        = string
  sensitive   = true
}

variable "ecr_repo_url" {
  description = "URL of the ECR repository containing the backend Docker image"
  type        = string
}

# (Security Groups and IAM roles omitted for brevity in MVP draft)
