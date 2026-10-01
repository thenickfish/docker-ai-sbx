variable "REGISTRY" { default = "ghcr.io/thenickfish" }
variable "GIT_SHA"  { default = "latest" }

# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.49.0" }
variable "RTK_COMMIT"  { default = "b1c0dc00649c50fbe8930f849c800d4d6ca12091" }

# renovate: datasource=github-tags depName=JuliusBrussee/caveman
variable "CAVEMAN_VERSION" { default = "v2.7.0" }
variable "CAVEMAN_COMMIT"  { default = "8b0c1d3699b8d83e87fe4605b378da20c41555e0" }

# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.18.3" }

# renovate: datasource=github-releases depName=daniel3303/ClaudeCodeStatusLine
variable "STATUSLINE_VERSION" { default = "v1.4.4" }
variable "STATUSLINE_COMMIT"  { default = "5da96959df726707fe8ff41c5645b4f7b8c7eac9" }

group "default" {
  targets = ["claude", "pi"]
}

target "_common" {
  platforms = ["linux/amd64", "linux/arm64"]
  args = {
    RTK_VERSION        = RTK_VERSION
    RTK_COMMIT         = RTK_COMMIT
    CAVEMAN_VERSION    = CAVEMAN_VERSION
    CAVEMAN_COMMIT     = CAVEMAN_COMMIT
    DEVBOX_VERSION     = DEVBOX_VERSION
    STATUSLINE_VERSION = STATUSLINE_VERSION
    STATUSLINE_COMMIT  = STATUSLINE_COMMIT
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
