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

package model

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// 基础模型
type BaseModel struct {
	// UUID 主键
	ID string `gorm:"primaryKey;type:char(36)" json:"id"`
	// 创建时间
	CreatedAt time.Time `json:"created_at"`
	// 更新时间
	UpdatedAt time.Time `json:"updated_at"`
	// 软删除标记
	DeletedAt time.Time `gorm:"index" json:"deleted_at,omitempty"`
}

func (m *BaseModel) BeforeCreate(tx *gorm.DB) error {
	id, err := uuid.NewUUID()
	if err != nil {
		return err
	}
	m.ID = id.String()
	return nil
}
