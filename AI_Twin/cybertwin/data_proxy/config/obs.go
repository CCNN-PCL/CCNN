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
	"log"

	"github.com/go-chassis/go-archaius"
)

// ObsAuthConfig represents OBS authentication configuration
type ObsAuthConfig struct {
	Endpoint  string `yaml:"endpoint"`
	AccessKey string `yaml:"accessKey"`
	SecretKey string `yaml:"secretKey"`
	Bucket    string `yaml:"bucket"`
}

var obsAuthConfig ObsAuthConfig

// readObsAuthConfigFromArchaius reads OBS configuration from archaius
func readObsAuthConfigFromArchaius() error {
	// Try to read from archaius
	if archaius.Exist("obs.endpoint") {
		obsAuthConfig.Endpoint = archaius.GetString("obs.endpoint", "")
	}
	if archaius.Exist("obs.accessKey") {
		obsAuthConfig.AccessKey = archaius.GetString("obs.accessKey", "")
	}
	if archaius.Exist("obs.secretKey") {
		obsAuthConfig.SecretKey = archaius.GetString("obs.secretKey", "")
	}
	if archaius.Exist("obs.bucket") {
		obsAuthConfig.Bucket = archaius.GetString("obs.bucket", "")
	}

	log.Printf("init obs config success %+v", &obsAuthConfig)
	return nil
}

// GetObsAuthConfig returns the OBS authentication configuration
func GetObsAuthConfig() ObsAuthConfig {
	return obsAuthConfig
}
