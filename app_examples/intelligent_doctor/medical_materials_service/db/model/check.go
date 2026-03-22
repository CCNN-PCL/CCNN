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

// 就诊检查记录表
// 某次就诊中的检查订单（关联就诊和检查项目）
type VisitCheck struct {
	BaseModel

	// 关联就诊UUID
	VisitID string `gorm:"type:char(36);not null" json:"visit_id"`
	// 检查类型："routine"（常规）/"image"（影像）
	CheckType string `gorm:"size:10;not null" json:"check_type"`
	// 申请时间（开单时间）
	ApplyTime time.Time `gorm:"not null" json:"apply_time"`
	// 申请医生
	ApplyDoctor string `gorm:"size:50" json:"apply_doctor,omitempty"`
	// 实际检查时间
	CheckTime *time.Time `gorm:"not null" json:"check_time,omitempty"`
	// 报告生成时间
	ReportTime *time.Time `gorm:"not null" json:"report_time,omitempty"`

	// 关联：根据CheckType区分子表，1次检查 → 多个文件（影像/化验单）
	RoutineCheck *RoutineCheck `gorm:"foreignKey:VisitCheckID" json:"routine_check,omitempty"` // 常规检查子表（CheckType="routine"时有效）
	ImageCheck   *ImageCheck   `gorm:"foreignKey:VisitCheckID" json:"image_check,omitempty"`   // 影像检查子表（CheckType="image"时有效）
}

// 常规检查子表：存储结构化数值结果
type RoutineCheck struct {
	BaseModel
	VisitCheckID string             `gorm:"type:char(36);uniqueIndex;not null" json:"visit_check_id"` // 关联基础检查表ID（一对一）
	Items        []RoutineCheckItem `gorm:"foreignKey:RoutineCheckID" json:"items"`                   // 检查项明细（如血常规的白细胞、红细胞）
	Conclusion   string             `gorm:"type:text" json:"conclusion,omitempty"`                    // 总体结论（如"未见明显异常"）
	Interpreter  string             `gorm:"size:50" json:"interpreter,omitempty"`                     // 解读医生
}

// 常规检查项明细：存储单个指标的数值
type RoutineCheckItem struct {
	BaseModel
	RoutineCheckID string `gorm:"type:char(36);not null" json:"routine_check_id"` // 关联常规检查子表ID
	IndicatorCode  string `gorm:"size:30;not null" json:"indicator_code"`         // 指标编码（如白细胞：WBC）
	IndicatorName  string `gorm:"size:50;not null" json:"indicator_name"`         // 指标名称（如"白细胞计数"）
	Value          string `gorm:"size:50;not null" json:"value"`                  // 指标值（如"5.6×10⁹/L"，支持数值+单位）
	ReferenceRange string `gorm:"size:50" json:"reference_range,omitempty"`       // 参考范围（如"4-10×10⁹/L"）
	AbnormalFlag   string `gorm:"size:256" json:"abnormal_flag,omitempty"`        // 异常标记（↑/↓/无）
}

// 3. 影像检查子表：存储影像文件关联信息
type ImageCheck struct {
	BaseModel
	VisitCheckID string      `gorm:"type:char(36);uniqueIndex;not null" json:"visit_check_id"` // 关联基础检查表ID（一对一）
	CheckFiles   []CheckFile `gorm:"foreignKey:ImageCheckID" json:"check_files,omitempty"`     // 关联影像文件（如DICOM、报告PDF）
	Conclusion   string      `gorm:"type:text" json:"conclusion,omitempty"`                    // 影像诊断结论（如"胸部CT未见明显占位性病变"）
	Interpreter  string      `gorm:"size:50" json:"interpreter,omitempty"`                     // 解读医生（如放射科医生）
}

// 检查文件表
// 影像文件元信息（实际文件存对象存储）
type CheckFile struct {
	BaseModel

	// 关联影像检查子表ID（仅影像检查用）
	ImageCheckID string `gorm:"type:char(36);not null" json:"image_check_id"`

	// 文件名（如"CT_20241022.dcm"）
	Filename string `gorm:"size:200;not null" json:"filename"`
	// 文件类型（如"dcm"、"pdf"）
	FileType string `gorm:"size:50;not null" json:"file_type"`
	// 文件大小（字节）
	FileSize int64 `json:"file_size"`
	// 文件的md5sum值
	FileMd5sum string `gorm:"size:128;not null" json:"file_md5sum"`
	// 存储路径（如OSS URL）
	StoragePath string `gorm:"size:500;not null" json:"storage_path"`
	// 描述（如"胸部CT-肺窗"）
	Description string `gorm:"size:200" json:"description,omitempty"`
	// 上传时间
	UploadTime time.Time `gorm:"not null" json:"upload_time"`
}
