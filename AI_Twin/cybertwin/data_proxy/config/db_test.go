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
	"testing"

	"github.com/go-chassis/go-archaius"
)

func TestDBConfig(t *testing.T) {
	requiredFile := []string{"./test/db.yaml"}
	err := archaius.Init(
		archaius.WithCommandLineSource(),
		archaius.WithMemorySource(),
		archaius.WithENVSource(),
		archaius.WithRequiredFiles(requiredFile))
	if err != nil {
		t.Errorf("init archaius error %v", err)
	}

	defer archaius.Clean()

	if err := readDBConfigFromArchaius(); err != nil {
		t.Errorf("read db config error %v", err)
	}

	dbconfig := GetDBConfig()
	if dbconfig.DBName != "test" || len(dbconfig.Addresses) != 2 || dbconfig.User != "test" || dbconfig.Password != "test_pw" {
		t.Error("read db base config error")
	}

	if !dbconfig.SSL.Enable || dbconfig.SSL.CAFile != "./ca_file" || dbconfig.SSL.CertFile != "./cert_file" || dbconfig.SSL.KeyFile != "./key_file" {
		t.Error("db ssl config error")
	}

	// default
	if dbconfig.TimeoutConfig.ConnTimeout != 10 || dbconfig.TimeoutConfig.ReadTimeout != 30 ||
		dbconfig.TimeoutConfig.WriteTimeout != 30 || dbconfig.TimeoutConfig.OpTimeout != 30 {
		t.Error("db timeout error")
	}
}
