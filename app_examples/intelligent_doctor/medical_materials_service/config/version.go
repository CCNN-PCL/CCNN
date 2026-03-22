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

// 版本信息变量，在编译时通过-ldflags注入
var (
	// Version 版本号
	Version = "0.0.0-dev"
	// BuildTime 构建时间
	BuildTime = "unknown"
	// GitCommit Git提交哈希
	GitCommit = "unknown"
	// GitBranch Git分支
	GitBranch = "unknown"
)

// GetVersionInfo 返回版本信息
func GetVersionInfo() map[string]string {
	return map[string]string{
		"version":    Version,
		"build_time": BuildTime,
		"git_commit": GitCommit,
		"git_branch": GitBranch,
	}
}

// PrintVersion 打印版本信息
func PrintVersion() string {
	return "MedicalMaterialsMcpService\n" +
		"Version:    " + Version + "\n" +
		"Build Time: " + BuildTime + "\n" +
		"Git Commit: " + GitCommit + "\n" +
		"Git Branch: " + GitBranch
}
