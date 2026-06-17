variable "REGISTRY" { default = "ghcr.io/thenickfish" }
variable "GIT_SHA"  { default = "latest" }

# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.42.3" }
variable "RTK_COMMIT"  { default = "de78d70aee86fe6b7b5c2462820a1b6c250d425b" }

# renovate: datasource=github-tags depName=JuliusBrussee/caveman
variable "CAVEMAN_VERSION" { default = "v1.8.2" }
variable "CAVEMAN_COMMIT"  { default = "63a91ecadbf4c4719a4602a5abb00883f9966034" }

# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.17.3" }

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
