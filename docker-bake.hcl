variable "REGISTRY" { default = "ghcr.io/thenickfish" }
variable "GIT_SHA"  { default = "latest" }

# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.45.0" }
variable "RTK_COMMIT"  { default = "b34be37caf3796b69a50952a28e60e32b5daad43" }

# renovate: datasource=github-tags depName=JuliusBrussee/caveman
variable "CAVEMAN_VERSION" { default = "v1.10.0" }
variable "CAVEMAN_COMMIT"  { default = "fcf7663366c217dc8f334a11028de52ed950ceab" }

# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.18.0" }

group "default" {
  targets = ["claude", "pi"]
}

target "_common" {
  platforms = ["linux/amd64", "linux/arm64"]
  args = {
    RTK_VERSION     = RTK_VERSION
    RTK_COMMIT      = RTK_COMMIT
    CAVEMAN_VERSION = CAVEMAN_VERSION
    CAVEMAN_COMMIT  = CAVEMAN_COMMIT
    DEVBOX_VERSION  = DEVBOX_VERSION
  }
}

target "claude" {
  inherits = ["_common"]
  context  = "./claude"
  tags = [
    "${REGISTRY}/docker-ai-sbx-claude:latest",
    "${REGISTRY}/docker-ai-sbx-claude:${GIT_SHA}",
  ]
}

target "claude-test" {
  inherits = ["claude"]
  target   = "test"
  tags     = []
  output   = ["type=cacheonly"]
}

target "pi" {
  inherits = ["_common"]
  context  = "./pi"
  tags = [
    "${REGISTRY}/docker-ai-sbx-pi:latest",
    "${REGISTRY}/docker-ai-sbx-pi:${GIT_SHA}",
  ]
}

target "claude-local" {
  inherits  = ["claude"]
  platforms = []
  tags      = ["sbx-claude:latest"]
}

target "pi-local" {
  inherits  = ["pi"]
  platforms = []
  tags      = ["sbx-pi:latest"]
}
