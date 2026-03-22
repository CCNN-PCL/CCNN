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

package db

import (
	"time"
)

// 医疗数据存储地址表
type MedicalDataStorage struct {
	ID                 int64  `gorm:"primaryKey;autoIncrement;column:id"`
	UserID             string `gorm:"column:user_id;type:varchar(64);index:idx_user_id;not null"`
	Location           string `json:"hospital_location"`
	HospitalName       string `gorm:"column:hospital_name;type:varchar(255)"`
	Department         string `gorm:"column:department;char(256)"`
	DataServiceAddress string `gorm:"column:dataservice_address;type:varchar(500)"`
	DataTypes          string `gorm:"column:data_types;type:varchar(1000)"` // JSON格式存储的数据类型
	// AccessToken     string    `gorm:"column:access_token;type:varchar(500)"`
	IsActive     bool      `gorm:"column:is_active;default:true"`
	LastSyncedAt time.Time `gorm:"column:last_synced_at"`
	CreatedAt    time.Time `gorm:"column:created_at;autoCreateTime"`
	UpdatedAt    time.Time `gorm:"column:updated_at;autoUpdateTime"`
}

func (MedicalDataStorage) TableName() string {
	return "medical_data_storage"
}
