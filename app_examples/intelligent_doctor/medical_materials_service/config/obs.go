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

var gObsConfig *OBSAuthConfig

type OBSAuthConfig struct {
	Endpoint  string `yaml:"obs.endpoint"`
	AccessKey string `yaml:"obs.access_key"`
	SecretKey string `yaml:"obs.secret_key"`
}

func GetObsAuthConfig() *OBSAuthConfig {
	return gObsConfig
}

func readObsAuthConfigFromArchaius() error {
	obsConfig := &OBSAuthConfig{}
	err := archaius.UnmarshalConfig(&obsConfig)
	if err != nil {
		return err
	}
	gObsConfig = obsConfig
	log.Printf("init obs config success %+v", gObsConfig)
	return nil
}
