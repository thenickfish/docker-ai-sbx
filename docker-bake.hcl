variable "REGISTRY"  { default = "ghcr.io/thenickfish" }
variable "GIT_SHA"   { default = "latest" }
variable "PLATFORMS" { default = "" }

# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.42.4" }
variable "RTK_COMMIT"  { default = "8a7dd7e5570d7744d4b6508479a3674fe8c49286" }

# renovate: datasource=github-tags depName=JuliusBrussee/caveman
variable "CAVEMAN_VERSION" { default = "v1.8.2" }
variable "CAVEMAN_COMMIT"  { default = "63a91ecadbf4c4719a4602a5abb00883f9966034" }

# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.17.3" }

# renovate: datasource=npm depName=renovate tracking=single
variable "RENOVATE_VERSION" { default = "43.236.0" }

# renovate: datasource=github-releases depName=docker/docker-ce tracking=single
variable "DOCKER_VERSION" { default = "29.6.0" }

group "default" {
  targets = ["claude", "pi"]
}

target "_common" {
  platforms = PLATFORMS != "" ? split(",", PLATFORMS) : []
  contexts = {
    root = "."
  }
  args = {
    RTK_VERSION      = RTK_VERSION
    RTK_COMMIT       = RTK_COMMIT
    CAVEMAN_VERSION  = CAVEMAN_VERSION
    CAVEMAN_COMMIT   = CAVEMAN_COMMIT
    DEVBOX_VERSION   = DEVBOX_VERSION
    RENOVATE_VERSION = RENOVATE_VERSION
    DOCKER_VERSION   = DOCKER_VERSION
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
