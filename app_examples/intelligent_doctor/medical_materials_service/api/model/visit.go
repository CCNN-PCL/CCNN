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

type QueryVisitsInfoRequest struct {
	UserID         string `json:"user_id" description:"查询就诊信息的用户ID"`
	IllnessKeyWord string `json:"illess_keyword,omitempty" description:"描述症状关键字，用于检索具有该特征症状的就诊信息"`
	Department     string `json:"department,omitempty" description:"就诊科室名称"`
	StartTime      string `json:"start_time,omitempty" description:"获取从该时间开始的就诊信息"`
}

type QueryVisitsInfoResponse struct {
	UserID string  `json:"user_id"`
	Visits []Visit `json:"visits"`
}

type Visit struct {
	// 就诊ID
	ID string `json:"id"`
	// 关联患者ID
	PatientID string `json:"patient_id"`
	Hospital  string `json:"hospital"`
	// 就诊类型（门诊/急诊/住院）
	VisitType string `json:"visit_type"`
	// 就诊科室（如"心内科"）
	Department string `json:"department"`
	// 接诊医生，先用医生名称表示
	DoctorID string `json:"doctor_id,omitempty"`
	// 就诊时间
	VisitTime time.Time `json:"visit_time"`

	// 病例信息
	// 患者主要症状, 就诊时主动陈述的最主要症状、体征及持续时间
	ChiefComplaint string `json:"chief_complaint"`
	// 现病史,描述患者从发病到就诊的全过程，包括症状的发生时间、性质、程度、演变规律、伴随症状、
	// 已采取的治疗及效果等，是对主诉的补充和细化，帮助医生判断病因和病情进展
	PresentIllness string `json:"present_illness"`
	// 辅助检查结果摘要, 就诊期间所做的实验室检查、影像学检查、器械检查等结果的摘要
	AuxiliaryExam string `json:"auxiliary_exam"`
	// 治疗方案
	TreatmentPlan string `json:"treatment_plan"`

	// 诊断
	Diagnoses []Diagnosis `json:"diagnoses,omitempty"`
	// 处方
	Prescriptions []Prescription `json:"prescriptions,omitempty"`
	// 检查
	VisitChecks []VisitCheck `json:"visit_checks,omitempty"`
}

// 诊断信息表, 每次就诊的诊断结果（支持多诊断）
type Diagnosis struct {
	// 疾病名称
	DiseaseName string `gorm:"size:100;not null" json:"disease_name"`
	// 是否主诊断
	IsMain bool `gorm:"default:false" json:"is_main"`
}

// 处方头信息
type Prescription struct {
	// 开方时间
	PrescribeTime time.Time `json:"prescribe_time"`
	// 药品类型（西药/中药）
	DrugType string `json:"drug_type"`

	// 药品明细
	DrugItems []PrescriptionDrug `json:"drug_items,omitempty"`
}

// 处方药品明细表
// 处方中的具体药品信息
type PrescriptionDrug struct {
	// 药品名称
	DrugName string `json:"drug_name"`
	// 规格（如"5mg/片"）
	Specification string `json:"specification"`
	// 单次剂量（如"1片"）
	Dosage string `json:"dosage"`
	// 频次（如"每日3次"）
	Frequency string `json:"frequency"`
	// 疗程（如"7天"）
	Course string `json:"course"`
	// 总数量
	TotalQuantity int `json:"total_quantity"`
	// 给药途径（如"口服"）
	Administration string `json:"administration"`
}

// 就诊检查记录表
// 某次就诊中的检查订单（关联就诊和检查项目）
type VisitCheck struct {
	ID string `json:"id"`
	// 检查类型："routine"（常规）/"image"（影像）
	CheckType string `json:"check_type"`
	// 申请时间（开单时间）
	ApplyTime time.Time `json:"apply_time"`
	// 申请医生
	ApplyDoctor string `json:"apply_doctor,omitempty"`
	// 实际检查时间
	CheckTime *time.Time `json:"check_time,omitempty"`
	// 报告生成时间
	ReportTime *time.Time `json:"report_time,omitempty"`
	// 常规检查子表（CheckType="routine"时有效）
	RoutineCheck *RoutineCheck `json:"routine_check,omitempty"`
	// 影像检查子表（CheckType="image"时有效）
	ImageCheck *ImageCheck `json:"image_check,omitempty"`
}

// 常规检查子表：存储结构化数值结果
type RoutineCheck struct {
	Items       []RoutineCheckItem `json:"items"`                 // 检查项明细（如血常规的白细胞、红细胞）
	Conclusion  string             `json:"conclusion,omitempty"`  // 总体结论（如"未见明显异常"）
	Interpreter string             `json:"interpreter,omitempty"` // 解读医生
}

// 常规检查项明细：存储单个指标的数值
type RoutineCheckItem struct {
	IndicatorCode  string `json:"indicator_code"`            // 指标编码（如白细胞：WBC）
	IndicatorName  string `json:"indicator_name"`            // 指标名称（如"白细胞计数"）
	Value          string `json:"value"`                     // 指标值（如"5.6×10⁹/L"，支持数值+单位）
	ReferenceRange string `json:"reference_range,omitempty"` // 参考范围（如"4-10×10⁹/L"）
	AbnormalFlag   string `json:"abnormal_flag,omitempty"`   // 异常标记（↑/↓/无）
}

// 3. 影像检查子表：存储影像文件关联信息
type ImageCheck struct {
	CheckFiles  []CheckFile `json:"check_files,omitempty"` // 关联影像文件（如DICOM、报告PDF）
	Conclusion  string      `json:"conclusion,omitempty"`  // 影像诊断结论（如"胸部CT未见明显占位性病变"）
	Interpreter string      `json:"interpreter,omitempty"` // 解读医生（如放射科医生）
}

// 检查文件表
// 影像文件元信息（实际文件存对象存储）
type CheckFile struct {
	ID string `json:"id"`

	// 文件名（如"CT_20241022.dcm"）
	Filename string `json:"filename"`
	// 文件类型（如"dcm"、"pdf"）
	FileType string `json:"file_type"`
	// 文件大小（字节）
	FileSize int64 `json:"file_size"`
	// 文件的md5sum值
	FileMd5sum string `json:"file_md5sum"`
	// 存储路径（如OSS URL）
	StoragePath string `json:"storage_path"`
	// 描述（如"胸部CT-肺窗"）
	Description string `json:"description,omitempty"`
	// 上传时间
	UploadTime time.Time `json:"upload_time"`
}
