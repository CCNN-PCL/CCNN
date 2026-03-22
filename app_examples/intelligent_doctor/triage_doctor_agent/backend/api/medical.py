# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
"""
医疗数据相关API
===============

提供医疗影像、病历等数据管理API接口

作者: QSIR
版本: 1.0
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import base64

from backend.services.medical_service import MedicalService
from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服务
medical_service = MedicalService()
auth_service = AuthService()

class MedicalImageResponse(BaseModel):
    """医疗影像响应模型"""
    image_id: str
    user_id: str
    hospital_id: str
    image_type: str
    image_category: str
    examination_date: str
    description: Optional[str] = None
    filename: Optional[str] = None
    upload_time: str
    file_size: int

class MedicalRecordResponse(BaseModel):
    """医疗记录响应模型"""
    record_id: str
    user_id: str
    hospital_id: str
    record_type: str
    description: Optional[str] = None
    filename: Optional[str] = None
    upload_time: str
    file_size: int

class ImageUploadResponse(BaseModel):
    """影像上传响应模型"""
    success: bool
    message: str
    image_id: Optional[str] = None
    image_info: Optional[MedicalImageResponse] = None

@router.post("/images/upload", response_model=ImageUploadResponse)
async def upload_medical_image(
    file: UploadFile = File(...),
    hospital_id: str = Form(...),
    image_type: str = Form(...),
    examination_date: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    上传医疗影像
    
    参数:
        file: 影像文件
        hospital_id: 医院ID
        image_type: 影像类型
        examination_date: 检查日期
        description: 影像描述
        current_user: 当前用户信息
        
    返回:
        ImageUploadResponse: 上传结果
    """
    try:
        logger.info(f"用户 {current_user.get('username')} 上传影像: {file.filename}")
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/dicom']
        content_type = file.content_type
        
        # 如果content_type为None，尝试根据文件名判断
        if content_type is None:
            if file.filename:
                filename_lower = file.filename.lower()
                if filename_lower.endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif filename_lower.endswith('.png'):
                    content_type = 'image/png'
                elif filename_lower.endswith('.dicom'):
                    content_type = 'image/dicom'
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {content_type}。支持的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小 (10MB限制)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过10MB限制"
            )
        
        # 上传影像
        result = await medical_service.upload_medical_image(
            user_id=current_user.get('user_id'),
            hospital_id=hospital_id,
            image_data=file_content,
            image_type=image_type,
            examination_date=examination_date,
            description=description,
            filename=file.filename
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', '上传失败')
            )
        
        return ImageUploadResponse(
            success=True,
            message="影像上传成功",
            image_id=result.get('image_id'),
            image_info=result.get('image_info')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"影像上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"影像上传失败: {str(e)}"
        )

@router.get("/images", response_model=List[MedicalImageResponse])
async def get_medical_images(
    hospital_id: Optional[str] = None,
    image_type: Optional[str] = None,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    获取医疗影像列表
    
    参数:
        hospital_id: 医院ID过滤
        image_type: 影像类型过滤
        current_user: 当前用户信息
        
    返回:
        List[MedicalImageResponse]: 影像列表
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"用户 {current_user.get('username')} 获取影像列表")
        
        # 获取影像列表
        images = await medical_service.get_medical_images(
            user_id=user_id,
            hospital_id=hospital_id,
            image_type=image_type
        )
        
        return images
        
    except Exception as e:
        logger.error(f"获取影像列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取影像列表失败: {str(e)}"
        )

@router.get("/images/{image_id}")
async def get_medical_image(
    image_id: str,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    获取指定医疗影像
    
    参数:
        image_id: 影像ID
        current_user: 当前用户信息
        
    返回:
        dict: 影像数据
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取影像数据
        image_data = await medical_service.get_medical_image(
            image_id=image_id,
            user_id=user_id
        )
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="影像不存在"
            )
        
        return image_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取影像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取影像失败: {str(e)}"
        )

@router.delete("/images/{image_id}")
async def delete_medical_image(
    image_id: str,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    删除医疗影像
    
    参数:
        image_id: 影像ID
        current_user: 当前用户信息
        
    返回:
        dict: 删除结果
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"用户 {current_user.get('username')} 删除影像: {image_id}")
        
        # 删除影像
        result = await medical_service.delete_medical_image(
            image_id=image_id,
            user_id=user_id
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "删除影像失败")
            )
        
        return {
            "message": "影像删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除影像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除影像失败: {str(e)}"
        )

@router.post("/records/upload")
async def upload_medical_record(
    file: UploadFile = File(...),
    hospital_id: str = Form(...),
    record_type: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    上传医疗记录
    
    参数:
        file: 记录文件
        hospital_id: 医院ID
        record_type: 记录类型
        description: 记录描述
        current_user: 当前用户信息
        
    返回:
        dict: 上传结果
    """
    try:
        logger.info(f"用户 {current_user.get('username')} 上传医疗记录: {file.filename}")
        
        # 验证文件类型
        allowed_types = ['application/pdf', 'text/plain', 'application/msword']
        content_type = file.content_type
        
        # 如果content_type为None，尝试根据文件名判断
        if content_type is None:
            if file.filename:
                filename_lower = file.filename.lower()
                if filename_lower.endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename_lower.endswith('.txt'):
                    content_type = 'text/plain'
                elif filename_lower.endswith(('.doc', '.docx')):
                    content_type = 'application/msword'
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {content_type}。支持的类型: {', '.join(allowed_types)}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 上传记录
        result = await medical_service.upload_medical_record(
            user_id=current_user.get('user_id'),
            hospital_id=hospital_id,
            record_data=file_content,
            record_type=record_type,
            description=description,
            filename=file.filename
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', '上传失败')
            )
        
        return {
            "success": True,
            "message": "医疗记录上传成功",
            "record_id": result.get('record_id')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"医疗记录上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"医疗记录上传失败: {str(e)}"
        )

@router.get("/records", response_model=List[MedicalRecordResponse])
async def get_medical_records(
    hospital_id: Optional[str] = None,
    record_type: Optional[str] = None,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    获取医疗记录列表
    
    参数:
        hospital_id: 医院ID过滤
        record_type: 记录类型过滤
        current_user: 当前用户信息
        
    返回:
        List[MedicalRecordResponse]: 记录列表
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取记录列表
        records = await medical_service.get_medical_records(
            user_id=user_id,
            hospital_id=hospital_id,
            record_type=record_type
        )
        
        return records
        
    except Exception as e:
        logger.error(f"获取医疗记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取医疗记录失败: {str(e)}"
        )

@router.get("/hospitals")
async def get_hospitals(current_user: dict = Depends(auth_service.get_current_user)):
    """
    获取医院列表
    
    参数:
        current_user: 当前用户信息
        
    返回:
        dict: 医院列表
    """
    try:
        # 获取医院列表
        hospitals = await medical_service.get_hospitals()
        
        return {
            "hospitals": hospitals
        }
        
    except Exception as e:
        logger.error(f"获取医院列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取医院列表失败: {str(e)}"
        )
