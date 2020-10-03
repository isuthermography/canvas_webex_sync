
class Participant(object):
    netid=None
    canvasid=None
    name=None
    short_name=None
    sortable_name=None
    type=None # "StudentEnrollment","TeacherEnrollment","TaEnrollment","DesignerEnrollment", or "ObserverEnrollment"
    canv_user=None # canvasapi User object
    canv_enrollment=None # canvasapi Enrollment object

    def __init__(self,**kwargs):
        # Set attributes according to constructor parameters
        for arg in kwargs:
            if not hasattr(self,arg):
                raise ValueError("participant does not have a %s attribute" % (arg))
            setattr(self,arg,kwargs[arg])
            pass
        pass
    def __repr__(self):
        return "Participant: \"%s\" %s" % (self.name,self.netid)
    pass


class Group(object):
    name=None
    part_by_netid=None
    canv_group=None # Canvas group object

    def __init__(self,**kwargs):
        self.part_by_netid={}
        # Set attributes according to constructor parameters
        for arg in kwargs:
            if not hasattr(self,arg):
                raise ValueError("participant does not have a %s attribute" % (arg))
            setattr(self,arg,kwargs[arg])
            pass
        pass
    def __repr__(self):
        return str(self.__dict__)
    pass
    
def canvas_participants(canvas,course):
    """canvas from Canvas(API_URL,API_KEY)
    course from canvas.get_course(course_number)
"""
    canvpart_by_netid={} # dictionary of participants
    canvpart_by_canvasid={}
    canvpart_by_sortablename={}
    canvpart_by_type={} # dictionary of list of participants
    for enrolled  in course.get_enrollments():
        if enrolled.user["name"]=="Test Student":
            # ignore test student account
            continue
        
        part = Participant(canvasid=enrolled.user["id"],
                           netid=enrolled.user["login_id"],
                           name=enrolled.user["name"],
                           short_name=enrolled.user["short_name"],
                           sortable_name=enrolled.user["sortable_name"],
                           type=enrolled.type,
                           canv_enrollment=enrolled,
                           canv_user=course.get_user(enrolled.user["id"]))
        
        canvpart_by_netid[part.netid]=part
        canvpart_by_canvasid[part.canvasid]=part
        canvpart_by_sortablename[part.sortable_name]=part
        if part.type not in canvpart_by_type:
            canvpart_by_type[part.type]=[]
            pass
        canvpart_by_type[part.type].append(part)
        pass
    return (canvpart_by_netid,canvpart_by_canvasid,canvpart_by_sortablename)

def course_by_name(canvas,course_name):
    matching_courses = [c for c in canvas.get_courses() if c.name==course_name]

    if len(matching_courses) != 1:
        raise ValueError("List of courses matching \"%s\" has length %d not 1" % (course_name,len(matching_courses)))
    
    course = matching_courses[0]
    return course

def canvas_groups(canvas,course,group_category_name,canvpart_by_canvasid):
    # Get group categories matching given category name
    group_categories = [ gc for gc in course.get_group_categories() if gc.name==group_category_name ] 
    if len(group_categories) < 1:
        raise ValueError("Group category (Group set) %s not found in course" % (group_category_name))
    elif len(group_categories) > 1:
        raise ValueError("Multiple group categories (Group sets) matching %s found in course" % (group_category_name))

    group_category=group_categories[0]
    
    
    groups_by_name={}
    
    for cgroup in course.get_groups():
        # Ignore groups not in our category of interest
        if cgroup.group_category_id != group_category.id:
            continue
        
        part_by_netid={}
        
        for memb in cgroup.get_memberships():
            participant = canvpart_by_canvasid[memb.user_id]

            part_by_netid[participant.netid]=participant
            pass
        group = Group(name=cgroup.name,part_by_netid=part_by_netid,canv_group=cgroup)
        groups_by_name[group.name]=group
        pass
    return groups_by_name


