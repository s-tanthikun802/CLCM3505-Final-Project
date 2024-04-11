provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_deployment" "deployment" {
  metadata {
    name = "clcm3505-final-project-deployment"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "clcm3505-final-project"
      }
    }

    template {
      metadata {
        labels = {
          app = "clcm3505-final-project"
        }
      }

      spec {
        container {
          image = "stanthikun802/clcm3505-final-project:latest"
          name  = "clcm3505-final-project"

          port {
            container_port = 80
          }

          env {
            name  = "ANTHROPIC_API_KEY"
            value = var.ANTHROPIC_API_KEY
          }

          env {
            name  = "GOOGLE_API_KEY"
            value = var.GOOGLE_API_KEY
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "service" {
  metadata {
    name = "clcm3505-final-project-service"
  }

  spec {
    selector = {
      app = "clcm3505-final-project"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}