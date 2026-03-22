/*
 * Copyright (c) 2026 PCL-CCNN
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package config

import (
	"fmt"
	"log"
)

// Build information variables
// These are set at compile time using ldflags
var (
	// Version is the version of the application
	Version string
	
	// Commit is the git commit hash
	Commit string
	
	// Branch is the git branch name
	Branch string
	
	// BuildTime is the time when the binary was built
	BuildTime string
)

// GetVersionInfo returns the build information
func GetVersionInfo() map[string]string {
	return map[string]string{
		"version":   Version,
		"commit":    Commit,
		"branch":    Branch,
		"buildTime": BuildTime,
	}
}

// GetVersionString returns a formatted version string
func GetVersionString() string {
	info := GetVersionInfo()
	
	// If version is not set (empty), it means we're running from source
	if info["version"] == "" {
		info["version"] = "development"
	}
	if info["commit"] == "" {
		info["commit"] = "unknown"
	}
	if info["branch"] == "" {
		info["branch"] = "unknown"
	}
	if info["buildTime"] == "" {
		info["buildTime"] = "unknown"
	}
	
	return fmt.Sprintf("Cybertwin DataProxy Service\nVersion: %s\nCommit: %s\nBranch: %s\nBuild Time: %s",
		info["version"], info["commit"], info["branch"], info["buildTime"])
}

// PrintVersion prints the version information to log
func PrintVersion() {
	log.Printf("Cybertwin DataProxy Service")
	log.Printf("Version: %s", getVersionField("version"))
	log.Printf("Commit: %s", getVersionField("commit"))
	log.Printf("Branch: %s", getVersionField("branch"))
	log.Printf("Build Time: %s", getVersionField("buildTime"))
}

// getVersionField returns the version field with fallback
func getVersionField(field string) string {
	info := GetVersionInfo()
	value := info[field]
	if value == "" {
		return "unknown"
	}
	return value
}
