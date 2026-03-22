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

import "time"

// 就诊人档案表
type Patient struct {
	BaseModel

	// 用户ID，关联用户信息
	UserID string `gorm:"type:char(36);uniqueIndex;not null" json:"user_id"`

	// 病历号（唯一标识），暂时没想到用处，但医疗系统都有这个标识, 先保留
	MedicalRecordNo string `gorm:"size:36;uniqueIndex;not null" json:"medical_record_no"`
	// 姓名
	Name string `gorm:"size:50;not null" json:"name"`
	// 性别
	Gender string `gorm:"size:2;check:gender IN ('男','女','未知')" json:"gender"`
	// 出生日期
	Birthday *time.Time `json:"birthday,omitempty"`
	// 身份证ID（唯一）
	IDCard string `gorm:"size:18;uniqueIndex" json:"id_card,omitempty"`
	// 联系电话
	Phone string `gorm:"size:20" json:"phone,omitempty"`
	// 家庭地址
	Address string `gorm:"size:200" json:"address,omitempty"`
	// 过敏史
	AllergyHistory string `gorm:"type:text" json:"allergy_history,omitempty"`
	// 既往病史
	MedicalHistory string `gorm:"type:text" json:"medical_history,omitempty"`
	// 家族病史
	FamilyMedicalHistory string `gorm:"type:text" json:"family_medical_history,omitempty"`
	// 紧急联系人
	EmergencyContact string `gorm:"size:50" json:"emergency_contact,omitempty"`
	// 紧急联系人电话
	EmergencyPhone string `gorm:"size:20" json:"emergency_phone,omitempty"`

	// 关联就诊记录信息 -> 1 ：n(一个患者有多次就诊记录)
	Vistits []Visit `gorm:"foreignKey:PatientID" json:"visits,omitempty"`
}
