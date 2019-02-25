from .models import *
from states.models import *
from django.db.models import Q
import random


def chapter_switch(user = None):
    '''This function checks the chapter 
    already assessed by student and then return the next chapter
    for which question are to be given'''
    completed_chapters = []
    list_of_chapters  = []
    
    if user:
        student_record = StudentStatus.objects.filter(user = user)
        for record in student_record:
            completed_chapters.append(record.chapter)
        standard = user.standard
        chapters = Chapter.objects.filter(standard = standard)
        for chapter in chapters:
            list_of_chapters.append(chapter)
        next_chapter = list(set(list_of_chapters) - set(completed_chapters))
        random.shuffle(next_chapter)
        if len(next_chapter) == 0:
            end_assessment(user)
            return -1
        else:
            print('chapter switch returned', next_chapter[0])
            a = next_chapter[0]
            return a
        



###########################__________ GET UNSOLVED QUESTION___________######################################
def getUnsolvedQuestion(user, state):
    '''
    It takes the state and checks all unsolved 
    question of that state and gives a random question
    from that. IT ALSO SAVES IT IN CURRENT QUESTION
    '''
    questions = AssessmentQuestion.objects.filter(state = state)
    solved = QuestionResponse.objects.filter(question__state = state)
    list_of_all_questions = []
    list_of_solved_questions = []
    for q in solved:
        list_of_solved_questions.append(q.question)
    for a in questions:
        list_of_all_questions.append(a)
    print('In getunsolvedquestion', list_of_solved_questions)
    print('list to do', state, user, list_of_all_questions )
    todo = list(set(list_of_all_questions) - set(list_of_solved_questions))
    random.shuffle(todo)
    print('TODO random question list is',todo)
    if len(todo) != 0:
        question = todo[0]
        current = CurrentQuestion.objects.filter(user = user)
        if current.exists():
            current = current.first()
            current.question = question
            current.save()
            return question
        else:
            CurrentQuestion.objects.create(
                user = user,
                question = question
            )
            return question
    else:
        return -1



def getUnsolvedQLoop(user, chapter, state, node):
    '''It chnges current question of user depending upno which were unsolved by him in
    given state else will go to next state and gives again unsolved questions'''

    question = getUnsolvedQuestion(user, state)
    print(question)
    if question==-1:
        print('In getunsolvedquestionLOOOOP')
        print('Details here are:----', state, user, node)
        state, node = switch_nodes(user, chapter, state, node, 1)
        if node==-1 or node == 6:
            return end_assessment(user)
        else:
            getUnsolvedQLoop(user, state, node)
    print('In loop final getunsolved questionloooop', question)
    return question

    ###########################__________ GET UNSOLVED QUESTION___________######################################





###########################__________ GET NODE_STATE___________######################################


def getNodeState(new_chapter = None, user = None):
    ''' It Gives appropriater Node and State of the new_chapter passed 
    in the function depending on total nodes present in the
    given new_chapter
    '''
    if new_chapter:
        print('In call just 1 GETNode state', new_chapter)
        state = State.objects.filter(chapter = new_chapter)
        number_of_states = len(state)//3
        print("Number of states in assigned node will be", number_of_states)
        if number_of_states==0:
            save_chapter(user, new_chapter)
            next_chapter_new = chapter_switch(user)
            if next_chapter_new == -1 or next_chapter_new == 6 :
                return end_assessment(user)
            else:
                return getNodeState(next_chapter_new, user)
        nodes = Node.objects.filter(state_node__chapter = new_chapter).distinct()
        if len(nodes)==0:
            save_chapter(user, new_chapter)
            next_chapter = chapter_switch(user)
            if next_chapter_new == -1 or next_chapter_new == 6:
                return end_assessment(user)
            else:
                return getNodeState(next_chapter_new, user)
        for node in nodes:
            if len(node.state_node.all()) == number_of_states:
                node_ = node
                break
        node_number = number_of_states//2 + 1
        for state_obj in node_.state_node.all():
            node_number = node_number -1
            if node_number ==0:
                break
        print('IN getNodestate about to   - save-----', state_obj,'------', node_)
        save_chapter(user, new_chapter, state_obj, node_)
        print('GETNODESTATE  returned', new_chapter, state_obj, node_)
        return state_obj, node_
    



###############################__________ OUTER _ FRINGE___________######################################


def outer_fringe(node):
    
    print('In outer fringe', node)  # gives outer fringe in consumable format
    
    ch= Chapter.objects.get(state=node.state_node.all()[0])
    size= node.state_node.all().count()
    
    fringe_outer= list()
    ch_nodes= Node.objects.filter(state_node__chapter=ch).distinct()  # take all nodes E chapter
    for nd in ch_nodes:
        if nd.state_node.all().count()== size+1:  # select ony those whos state count is one more than curr nodes state count
            a_match=1
            for st_curr in node.state_node.all():     # check whether every state E curr_node in potential next_node
                st_matches=0
                for st_next in nd.state_node.all():
                    if st_curr.id == st_next.id:
                        st_matches=1
                if st_matches== 0:
                    a_match=0
            if a_match ==1:
                fringe_outer.append(nd)

    return fringe_outer    
            


def random_outer_fringe(node):
    ''' 
    It shuffles all outer fringe possible and select only one node
     from all possible outer fringes of a node
    '''
    outer_fringe_ = outer_fringe(node)
    if len(outer_fringe_) == 0:
        return -1
    
    random.shuffle(outer_fringe_)
    first_item =  outer_fringe_[0]
    return first_item


def surplus_state(source_node, dest_node):  
    sl= source_node.state_node.all().count()
    dl= dest_node.state_node.all().count()
    (smaller, larger)= (source_node, dest_node) if sl<dl else (dest_node, source_node)
    print("am in %s.. going to %s"%(str(source_node), str(dest_node))) #**************************************************
    for lg_st in larger.state_node.all():          
        matched=0
        for sm_st in smaller.state_node.all():   # matching each state of larger node with all states of smaller one. The state which doesnt matches is the result
            if sm_st.id == lg_st.id:
                matched=1
        if matched == 0:
            return lg_st





def random_surplus_state(node):
    '''
The main Parent highest level function driving all others. It takes a node and gives its
its outer fringe node if possible totally random else returns -1
IT ALSO SAVES IN STUDENTSTATUS
    '''
    dest_node = random_outer_fringe(node)
    if dest_node == -1:
        return -1, -1
    return surplus_state(node, dest_node), dest_node



def switch_nodes(user, chapter, state, node, jump):
    print(jump, int(jump))
 
    if int(jump) == 0:
        # give the same state and node once again to the student
        return state, node 
    
    if int(jump) > 0:
        print('In switch node jump 1-1', chapter, state, user, node)
        outer_fringe_state, outer_fringe_node = random_surplus_state(node)
        if outer_fringe_node != -1:
            print('Got, In switch nodes block of switch nodes', outer_fringe_state)
            status = StudentStatus.objects.filter( Q(user = user) & Q(chapter = chapter) )
            if status.exists():
                status = status.first()
                status.node = outer_fringe_node
                status.state = outer_fringe_state
                status.score = 0
                status.save()
                print(status.node)
                print('Next state is', status.state)
                return status.state, status.node
            else:
                StudentStatus.objects.create(
                    user = user,
                    state = outer_fringe_state,
                    node = outer_fringe_node,
                    chapter = chapter
                )
        else:
            print('In switch node, going to next chapter', chapter, state, node)
            save_chapter(user, chapter, state, node)
            print(chapter_switch(user))
            print('sdfsdf')
            next_chapter_new = chapter_switch(user)
            if next_chapter_new == -1 or next_chapter_new == 6:
                return end_assessment(user)
            else:
                print('In switch node, next chapter found is', next_chapter_new)
                return getNodeState(next_chapter_new, user)


 

    if int(jump) < 0:
            print('In JUMP -2 small last switch node, going to next chapter', jump, chapter, state, node)
            save_chapter(user, chapter, state, node)
            next_chapter_new = chapter_switch(user)
            if next_chapter_new == -1 or next_chapter_new == 6:
                return end_assessment(user)
            else:
                print('In switch node, next chapter found is', next_chapter_new)
                return getNodeState(next_chapter_new, user)



###########################_______________________________________________________________######################################        


            




def save_chapter(user, chapter, state=None, node = None):
    ''' To save the data in student status with or without state and node provided'''

    print('In save chaper ', user, chapter, state, '------', node)
    old = StudentStatus.objects.filter(Q(user= user) & Q(chapter = chapter))
    if old.exists():
        print('Old student status in save_chapter existing')
        old = old.first()
        if state and node:
            old.state = state
            old.node = node
            old.score = 0
        else:
            old.score = 0
            old.empty = True
        old.save()

        
    else:
        StudentStatus.objects.create(
            user = user,
            chapter = chapter,
            state = state,
            node = node
        )
    return True

def end_assessment(user = None):
    # SAVE SOME DATA LATER SO THAT STUDENT CAN GIVE ASSESSMRNT ONLY ONCE
    return 6, 6
        

       

