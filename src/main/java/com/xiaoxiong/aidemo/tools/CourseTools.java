package com.xiaoxiong.aidemo.tools;

import com.baomidou.mybatisplus.extension.conditions.query.QueryChainWrapper;
import com.xiaoxiong.aidemo.entity.po.Course;
import com.xiaoxiong.aidemo.entity.po.CourseReservation;
import com.xiaoxiong.aidemo.entity.po.School;
import com.xiaoxiong.aidemo.entity.query.CourseQuery;
import com.xiaoxiong.aidemo.service.ICourseReservationService;
import com.xiaoxiong.aidemo.service.ICourseService;
import com.xiaoxiong.aidemo.service.ISchoolService;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.List;

@RequiredArgsConstructor
@Component
public class CourseTools {

    private final ICourseService courseService;
    private final ISchoolService schoolService;
    private final ICourseReservationService courseReservationService;

    @Tool(description = "根据条件查询课程")
    public List<Course> queryCourse(@ToolParam(required = false, description = "课程查询条件") CourseQuery query) {
        if (query == null) {
            return courseService.list();
        }
        QueryChainWrapper<Course> wrapper = courseService.query()
                .eq(query.getType() != null, "type", query.getType())
                .le(query.getEdu() != null, "edu", query.getEdu());
        if (query.getSorts() != null && !query.getSorts().isEmpty()) {
            for (CourseQuery.Sort sort : query.getSorts()) {
                wrapper.orderBy(true, sort.getAsc(), sort.getField());
            }
        }
        return wrapper.list();
    }

    @Tool(description = "查询所有校区")
    public List<School> queryAllSchools() {
        return schoolService.list();
    }

    @Tool(description = "查询课程预约单")
    public CourseReservation queryCourseReservation(Integer id) {
        return courseReservationService.getById(id);}

    @Tool(description = "生成课程预约单，并返回生成的预约单号")
    public Integer generateCourseReservation(
            @ToolParam(description = "预约课程") String course,
            @ToolParam(description = "预约校区") String school,
            @ToolParam(description = "学生姓名") String studentName,
            @ToolParam(description = "联系电话") String contactInfo,
            @ToolParam(description = "备注", required = false) String remark) {
        CourseReservation courseReservation = new CourseReservation();
        courseReservation.setCourse(course);
        courseReservation.setSchool(school);
        courseReservation.setStudentName(studentName);
        courseReservation.setContactInfo(contactInfo);
        courseReservation.setRemark(remark);
        courseReservationService.save(courseReservation);
        return courseReservation.getId();
    }
}
