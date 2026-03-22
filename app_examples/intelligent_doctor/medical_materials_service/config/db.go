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

var gDBConfig *DBConfig = &DBConfig{
	TimeoutConfig: TimeoutConfig{
		ConnTimeout:  10,
		ReadTimeout:  30,
		WriteTimeout: 30,
		OpTimeout:    30,
	},
	PoolConfig: PoolConfig{
		MaxOpenConns:    1000,
		MaxIdleConns:    1000 / 5,
		ConnMaxLifetime: 3600,
		ConnMaxIdletime: 30 * 60,
	},
}

type DBConfig struct {
	User          string        `yaml:"db.user"`
	Password      string        `yaml:"db.password"`
	Addresses     []string      `yaml:"db.addresses"`
	DBName        string        `yaml:"db.db_name"`
	SSL           SSLConfig     `yaml:"db.ssl"`
	TimeoutConfig TimeoutConfig `yaml:"db.timeout_config"`
	PoolConfig    PoolConfig    `yaml:"db.pool"`
}

// TimeoutConfig 超时参数
type TimeoutConfig struct {
	ConnTimeout  int `yaml:"conn_timeout"`  // 连接超时（默认10s）
	ReadTimeout  int `yaml:"read_timeout"`  // 读超时（默认30s）
	WriteTimeout int `yaml:"write_timeout"` // 写超时（默认30s）
	OpTimeout    int `yaml:"op_timeout"`    // 单个SQL操作超时（默认30s）
}

// PoolConfig 连接池配置
type PoolConfig struct {
	MaxOpenConns    int `yaml:"max_open_conns"`     // 最大打开连接数, default: 1000
	MaxIdleConns    int `yaml:"max_idle_conns"`     // 最大空闲连接数, default: 200
	ConnMaxLifetime int `yaml:"conn_max_life_time"` // 连接最大存活时间, default: 1小时
	ConnMaxIdletime int `yaml:"conn_max_idle_time"` // 连接最大空闲时间, default: 30分钟
}

type SSLConfig struct {
	Enable   bool   `yaml:"enable"`    // 是否开启SSL
	CAFile   string `yaml:"ca_file"`   // 根证书路径（ca.pem）
	CertFile string `yaml:"cert_file"` // 客户端证书路径（client-cert.pem）
	KeyFile  string `yaml:"key_file"`  // 客户端私钥路径（client-key.pem）
}

func GetDBConfig() *DBConfig {
	return gDBConfig
}

func readDBConfigFromArchaius() error {
	dbConfig := *gDBConfig
	err := archaius.UnmarshalConfig(&dbConfig)
	if err != nil {
		return err
	}
	gDBConfig = &dbConfig
	log.Printf("init db config success %+v", gDBConfig)
	return nil
}
