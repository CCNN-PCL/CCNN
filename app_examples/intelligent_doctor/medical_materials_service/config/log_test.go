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

func TestLogConfig(t *testing.T) {
	requiredFile := []string{"./test/log.yaml"}
	err := archaius.Init(
		archaius.WithCommandLineSource(),
		archaius.WithMemorySource(),
		archaius.WithENVSource(),
		archaius.WithRequiredFiles(requiredFile))
	if err != nil {
		t.Errorf("init archaius error %v", err)
	}

	if err := readLogConfigFromArchaius(); err != nil {
		t.Errorf("read log config error %v", err)
	}

	logConfig := GetLogConfig()
	if logConfig.FilePath != "./test.log" || !logConfig.Debug || !logConfig.Verbose {
		t.Error("log config error")
	}
}
