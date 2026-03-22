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

// 就诊记录表
type Visit struct {
	BaseModel

	// 关联患者ID
	PatientID string `gorm:"type:char(36);not null" json:"patient_id"`
	Hospital  string `gorm:"type:char(50);not null" json:"hospital"`
	// 就诊类型（门诊/急诊/住院）
	VisitType string `gorm:"size:20;not null" json:"visit_type"`
	// 就诊科室（如"心内科"）
	Department string `gorm:"size:50;not null" json:"department"`
	// 接诊医生，先用医生名称表示
	DoctorID string `gorm:"type:char(36)" json:"doctor_id,omitempty"`
	// 就诊时间
	VisitTime time.Time `gorm:"not null" json:"visit_time"`

	// 病例信息
	// 患者主要症状, 就诊时主动陈述的最主要症状、体征及持续时间
	ChiefComplaint string `gorm:"type:text;not null" json:"chief_complaint"`
	// 现病史,描述患者从发病到就诊的全过程，包括症状的发生时间、性质、程度、演变规律、伴随症状、
	// 已采取的治疗及效果等，是对主诉的补充和细化，帮助医生判断病因和病情进展
	PresentIllness string `gorm:"type:text" json:"present_illness"`
	// 辅助检查结果摘要, 就诊期间所做的实验室检查、影像学检查、器械检查等结果的摘要
	AuxiliaryExam string `gorm:"type:text" json:"auxiliary_exam"`
	// 治疗方案
	TreatmentPlan string `gorm:"type:text" json:"treatment_plan"`

	// 关联:1次就诊 -> 多个诊断 + 多个处方 + 多个检查
	Diagnoses       []Diagnosis      `gorm:"foreignKey:VisitID" json:"diagnoses,omitempty"`
	Prescriptions   []Prescription   `gorm:"foreignKey:VisitID" json:"prescriptions,omitempty"`
	VisitChecks     []VisitCheck     `gorm:"foreignKey:VisitID" json:"visit_checks,omitempty"`
	SurgicalRecords []SurgicalRecord `gorm:"foreignKey:VisitID" json:"surgical_record"`
}

// 诊断信息表, 每次就诊的诊断结果（支持多诊断）
type Diagnosis struct {
	BaseModel

	// 关联就诊UUID
	VisitID string `gorm:"type:char(36);not null" json:"visit_id"`
	// 疾病名称
	DiseaseName string `gorm:"size:100;not null" json:"disease_name"`
	// 是否主诊断
	IsMain bool `gorm:"default:false" json:"is_main"`
}

// 处方头信息
type Prescription struct {
	BaseModel

	// 关联就诊UUID
	VisitID string `gorm:"type:char(36);not null" json:"visit_id"`
	// 开方时间
	PrescribeTime time.Time `gorm:"not null" json:"prescribe_time"`
	// 药品类型（西药/中药）
	DrugType string `gorm:"size:20" json:"drug_type"`

	// 关联：1个处方 → 多个药品明细
	DrugItems []PrescriptionDrug `gorm:"foreignKey:PrescriptionID" json:"drug_items,omitempty"`
}

// 处方药品明细表（PrescriptionDrug）
// 处方中的具体药品信息
type PrescriptionDrug struct {
	BaseModel

	// 关联处方UUID
	PrescriptionID string `gorm:"type:char(36);not null" json:"prescription_id"`
	// 药品名称
	DrugName string `gorm:"size:100;not null" json:"drug_name"`
	// 药品用途
	Purpose string `gorm:"size:100;not null" json:"purpose"`

	// 规格（如"5mg/片"）
	Specification string `gorm:"size:50" json:"specification"`
	// 单次剂量（如"1片"）
	Dosage string `gorm:"size:20" json:"dosage"`
	// 频次（如"每日3次"）
	Frequency string `gorm:"size:20" json:"frequency"`
	// 疗程（如"7天"）
	Course string `gorm:"size:20" json:"course"`
	// 总数量
	TotalQuantity int `gorm:"not null" json:"total_quantity"`
	// 给药途径（如"口服"）
	Administration string `gorm:"size:50" json:"administration"`
}

type SurgicalRecord struct {
	BaseModel

	// 关联就诊UUID
	VisitID        string    `gorm:"type:char(36);not null" json:"visit_id"`
	SurgicalName   string    `gorm:"type:char(255)" json:"surgical_name"`
	SurgicalDate   time.Time `gorm:"not null" json:"surgical_date"`
	Surgeon        string    `gorm:"type:char(36);not null" json:"surgeon"`
	SurgicalResult string    `gorm:"type:text;not null" json:"surgical_result"`
}
