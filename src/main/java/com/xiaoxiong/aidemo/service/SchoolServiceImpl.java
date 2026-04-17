package com.xiaoxiong.aidemo.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xiaoxiong.aidemo.entity.po.School;
import com.xiaoxiong.aidemo.mapper.SchoolMapper;
import org.springframework.stereotype.Service;

/**
 * 校区表 服务实现类
 */
@Service
public class SchoolServiceImpl extends ServiceImpl<SchoolMapper, School> implements ISchoolService {

}
