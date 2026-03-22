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

type QueryPatientProfileRequest struct {
	UserID string `json:"user_id"`
}

type QueryPatientProfileResponse struct {
	// 就诊人ID
	ID string `json:"id"`
	// 用户ID，关联用户信息
	UserID string `json:"user_id"`

	// 病历号（唯一标识），暂时没想到用处，但医疗系统都有这个标识, 先保留
	MedicalRecordNo string `json:"medical_record_no"`
	// 姓名
	Name string `json:"name"`
	// 性别
	Gender string `json:"gender"`
	// 出生日期
	Birthday string `json:"birthday"`
	// 身份证ID（唯一）
	IDCard string `json:"id_card"`
	// 联系电话
	Phone string `json:"phone"`
	// 家庭地址
	Address string `json:"address"`
	// 过敏史
	AllergyHistory string `json:"allergy_history"`
	// 既往病史
	MedicalHistory string `json:"medical_history"`
	// 紧急联系人
	EmergencyContact string `json:"emergency_contact"`
	// 紧急联系人电话
	EmergencyPhone string `json:"emergency_phone"`
}

type QueryPatientMedicalInfoRequest struct {
	RequestID  string `json:"request_id"`
	UserID     string `json:"user_id"`
	Department string `json:"department" description:"就诊科室名称"`
	StartTime  string `json:"start_time,omitempty" description:"获取从该时间开始的就诊信息"`
}

type QueryPatientMedicalInfoResponse struct {
	RequestID   string      `json:"request_id"`
	MedicalData MedicalData `json:"medical_data"`
}

type MedicalData struct {
	MedicalHistory  MedicalHistory   `json:"medical_history"`
	Medications     []Medication     `json:"medications,omitempty"`
	LabResults      []LabResult      `json:"lab_results,omitempty"`
	ImageingData    []ImageingData   `json:"image_data,omitempty"`
	SurgicalRecords []SurgicalRecord `json:"surgical_records,omitempty"`
	Source          []string         `json:"source,omitempty"`
}

type MedicalHistory struct {
	ChronicDiseases    string              `json:"chronic_diseases"`
	FamilyHistory      string              `json:"family_history"`
	Allergies          string              `json:"allergies"`
	PreviousConditions []PreviousCondition `json:"previous_conditions,omitempty"`
	LastUpdate         *time.Time          `json:"last_update"`
}

type PreviousCondition struct {
	Condition     string `json:"condition"`
	DiagnosedDate string `json:"diagnosed_date"`
	Status        string `json:"status"`
}

type Medication struct {
	MedicationName string `json:"medication_name"`
	Dosage         string `json:"dosage"`
	Course         string `json:"course"`
	Frequency      string `json:"frequency"`
	StartDate      string `json:"start_date"`
	Purpose        string `json:"purpose"`
	Hospital       string `json:"hospital"`
}

type LabResult struct {
	TestName       string `json:"test_name"`
	Result         string `json:"result"`
	Unit           string `json:"unit"`
	ReferenceRange string `json:"reference_range"`
	Status         string `json:"status"`
	TestDate       string `json:"test_date"`
	Hospital       string `json:"hospital"`
}

type ImageingData struct {
	ImMagingID      string `json:"imageing_id"`
	ImagingType     string `json:"imaging_type"`
	ExaminationDate string `josn:"examination_date"`
	Findings        string `json:"findings"`
	Conclusion      string `json:"conclusion"`
	ImageUrl        string `json:"image_url"`
	Hospital        string `json:"hospital"`
}

type SurgicalRecord struct {
	SurgeryName string `json:"surgery_name"`
	SurgeryDate string `json:"surgery_date"`
	Hospital    string `json:"hospital"`
	Surgeon     string `json:"surgeon"`
	Status      string `json:"status"`
}
