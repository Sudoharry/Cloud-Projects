import pytest
from app import select_services

def test_select_services_microservices():
    services = select_services("Microservices", "High", "SQL")
    assert "EKS or ECS" in services
    assert "ALB + Auto Scaling + CloudFront" in services
    assert "RDS or Aurora" in services

def test_select_services_serverless():
    services = select_services("Serverless", "Low", "NoSQL")
    assert "AWS Lambda" in services
    assert "DynamoDB" in services