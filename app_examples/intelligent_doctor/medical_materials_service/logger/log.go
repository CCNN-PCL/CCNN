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

package logger

import (
	"io"
	"os"

	"github.com/sirupsen/logrus"

	lWriter "github.com/sirupsen/logrus/hooks/writer"
	"gopkg.in/natefinch/lumberjack.v2"
)

var Log *logrus.Logger

func init() {
	l := logrus.New()
	l.SetOutput(io.Discard)
	l.SetReportCaller(true)
	Log = l
}

func InitLogger(filePath string, verbose bool, debug bool, hook logrus.Hook) error {
	l := logrus.New()
	l.Level = logrus.DebugLevel
	l.SetReportCaller(true)
	l.SetOutput(io.Discard)

	l.Formatter = &logrus.TextFormatter{PadLevelText: true, FullTimestamp: true, ForceColors: false}

	levels := []logrus.Level{
		logrus.PanicLevel,
		logrus.FatalLevel,
		logrus.ErrorLevel,
		logrus.WarnLevel,
	}
	if debug {
		levels = append(levels, logrus.InfoLevel, logrus.DebugLevel)
	} else if verbose {
		levels = append(levels, logrus.InfoLevel)
	}

	// 配置 lumberjack 日志写入器
	logWriter := &lumberjack.Logger{
		Filename:   filePath, // 日志文件路径
		MaxSize:    100,      // 单个文件最大尺寸（MB）
		MaxBackups: 10,       // 最多保留 10 个备份文件
		MaxAge:     7,        // 日志文件保留 7 天
		Compress:   true,     // 压缩旧日志（.gz 格式）
	}
	writers := []io.Writer{logWriter, os.Stdout}

	l.AddHook(&lWriter.Hook{
		Writer:    io.MultiWriter(writers...),
		LogLevels: levels,
	})

	if hook != nil {
		l.AddHook(hook)
	}
	Log = l
	return nil
}
