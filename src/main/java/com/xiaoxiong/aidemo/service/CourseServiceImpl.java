package com.xiaoxiong.aidemo.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xiaoxiong.aidemo.entity.po.Course;
import com.xiaoxiong.aidemo.mapper.CourseMapper;
import org.springframework.stereotype.Service;

/**
 * 学科表 服务实现类
 */
@Service
public class CourseServiceImpl extends ServiceImpl<CourseMapper, Course> implements ICourseService {

}
