package com.xiaoxiong.aidemo.service;

import com.xiaoxiong.aidemo.entity.po.CourseReservation;
import com.xiaoxiong.aidemo.mapper.CourseReservationMapper;
import com.xiaoxiong.aidemo.service.ICourseReservationService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 *  课程预约表 服务实现类
 */
@Service
public class CourseReservationServiceImpl extends ServiceImpl<CourseReservationMapper, CourseReservation> implements ICourseReservationService {

}
