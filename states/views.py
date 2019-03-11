from django.shortcuts import render, redirect
from kst.models import *
from .models import *
from kst.utils import *


def learning(request):
    if request.user.is_authenticated:
        current_chapter = chapter_switch(request.user)
        if current_chapter:
            print('current chapter Learning', current_chapter)
            if current_chapter == -1:
                print("no further chaper")
            else:

                state, node = getNodeState(current_chapter, request.user)
                if state == 6:
                    return redirect('check:result')
                else:
                    print(state, node)
                    return render(request, 'states/learning.html', context)

        pass

    else:
        return redirect('account:login')
