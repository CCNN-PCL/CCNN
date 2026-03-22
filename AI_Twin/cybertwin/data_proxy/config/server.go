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

var gServerConfig *ServerConfig

type ServerConfig struct {
	Address string `yaml:"server.address"`
}

func GetServerConfig() *ServerConfig {
	return gServerConfig
}

func readServerConfigFromArchaius() error {
	config := &ServerConfig{}
	err := archaius.UnmarshalConfig(&config)
	if err != nil {
		return err
	}
	gServerConfig = config
	log.Printf("init server config success %+v", gServerConfig)
	return nil
}
